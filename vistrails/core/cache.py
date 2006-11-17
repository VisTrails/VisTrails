"""Cache Manager

The Cache Manager stores the previously executed results of VTK operations,
so that there will be as little overhead as possible in the execution
of pipelines with overlapping dataflows.

"""
import sha

import __builtin__
from core import system

from core.debug import DebugPrint
from core.utils import *
from core.vis_types import VistrailModuleType

################################################################################

def hashList(lst, hasher_f):
    hasher = sha.new()
    hash_l = [hasher_f(el) for el in lst]
    hash_l.sort()
    [hasher.update(hel) for hel in hash_l]
    return hasher.digest()

################################################################################

class CacheManager(object):
    def __init__(self):
        self.lowestTimeThreshold = 0.01
        self.lowestEfficiencyThreshold = 1e-5
        self.initMemoryLimits()
        self.clear()
        
    def touch(self):
        """touch() -> int - Bumps a touch time counter and returns the value."""
        self.touchTime += 1
        return self.touchTime

    def initMemoryLimits(self):
        """initMemoryLimits() -> None - tries to guess 'reasonable' memory limits
and set them. 'Reasonable' here means 25% of total estimated memory for maximum
memory, and 5% for post-flush use"""
        totalMemory = system.guessTotalMemory()
        if totalMemory == -1:
            DebugPrint.critical('Could not guess totalMemory! Cache has no limit in size')
            self.maxMemory = 300000
            self.minMemory = 100000
        else:
            self.maxMemory = totalMemory / 4
            self.minMemory = totalMemory / 20
            DebugPrint.log('Set cache minMemory to %s' % self.minMemory)
            DebugPrint.log('Set cache maxMemory to %s' % self.maxMemory)

    def addEntry(self, pipeline, result, elapsedTime, fixtureCreator):
        """addEntry(pipeline, result, time, fixtureCreator) -> None
Adds a new entry in the cache  if the entry passes efficiency and time constraints."""
        key = self.computeHash(pipeline)
        fixture = fixtureCreator(result)
        if self.cache.has_key(key):
            DebugPrint().warning('Pipeline already in cache\n')
            return fixture
        if elapsedTime < self.lowestTimeThreshold:
            DebugPrint().log('Entry time below threshold - not caching')
            return fixture
        use = sum(vtk_rtti.VTKRTTI.memoryUse(r) for r in result)
        efficiency = elapsedTime / use
        if efficiency < self.lowestEfficiencyThreshold:
            DebugPrint().log('Efficiency below threshold - not caching')
            return fixture
        self.cache[key] = (fixture, elapsedTime, use, self.touch())
        self.totalMemoryUse += use
        self.flush()
        return fixture
        
    def entriesByEfficiency(self):
        """entriesByEfficiency() -> [(efficiency, (key, entry))]
Returns a list of all cache entries sorted by efficiency (time/memory)."""
        lst = [(elapsedTime / memory, (item, (result, elapsedTime, memory, touch)))
               for (item, (result, elapsedTime, memory, touch)) in self.cache.iteritems()]
        lst.sort()
        return lst

    def entriesByLRU(self):
        """entriesByLRU() -> [(touchtime, (key, entry))]
Returns a list of all cache entries sorted by Least Recently Used."""
        lst = [(touch, (item, (result, elapsedTime, memory, touch)))
               for (item, (result, elapsedTime, memory, touch)) in self.cache.iteritems()]
        lst.sort()
        return lst

    def flush(self, flushByEfficiency=True):
        """flush(flushByEfficiency=True) -> None
Flushes the cache down to self.minMemory, if total memory use is larger than
self.maxMemory. If flushByEfficiency is true, flushes least efficient items, else
flushes by LRU items."""
        if self.maxMemory == -1:
            return
        if self.totalMemoryUse < self.maxMemory:
            return
        f = (self.totalMemoryUse, self.maxMemory, self.minMemory)
        s = 'Cache is too full (%s kB > %s kB): Will purge down to less than (%s kB)' % f
        DebugPrint().log(s)

        if flushByEfficiency:
            DebugPrint().critical('Will flush cache by efficiency.')
            lst = self.entriesByEfficiency()
            for (e, (k, v)) in lst:
                if self.totalMemoryUse <= self.minMemory:
                    return
                del self.cache[k]
                self.totalMemoryUse -= v[2]
        else:
            DebugPrint().critical('Will flush cache by LRU.')
            lst = self.entriesByLRU()
            for (e, (k, v)) in lst:
                if self.totalMemoryUse <= self.minMemory:
                    return
                del self.cache[k]
                self.totalMemoryUse -= v[2]
        

    def hasEntry(self, pipeline):
        """hasEntry(pipeline) -> bool - returns whether pipeline has a result computed
in the cache."""
        key = self.computeHash(pipeline)
        return self.cache.has_key(key)

    def getEntry(self, pipeline):
        """getEntry(pipeline) -> (object, time, memory, touch) -
returns cache entry for pipeline. pipeline must have an entry in the cache."""
        key = self.computeHash(pipeline)
        result = self.cache[key]
        newentry = (result[0], result[1], result[2], self.touch())
        self.cache[key] = newentry
        return newentry

    def clear(self):
        """clear() -> None - Completely clears the cache."""
        self.cache = {}
        self.totalMemoryUse = 0
        self.touchTime = 0

    def getMemoryUse(self, entry):
        if type(entry) == __builtin__.list:
            return sum([vtk_rtti.VTKRTTI.memoryUse(obj) for obj in lst])
        else:
            return vtk_rtti.VTKRTTI.memoryUse(entry)

    def examine(self):
        lst = self.entriesByEfficiency()
        for i in lst:
            print "----- Entry Description"
            print "   Efficiency: %s" % i[0]
            print "   Compute time: %.3f seconds" % i[1][1][1]
            print "   Memory consumption: %s kB" % i[1][1][2]
            print "   Touch time: %s" % i[1][1][3]
        print "Cache size: %s kB" % sum([i[1][2] for i in self.cache.iteritems()])

    def computeHash(self, pipeline):
        taggedModuleIds = [(self.uniqueIdModule(m), m.id)
                           for m in pipeline.modules.itervalues()]
        taggedModuleIds.sort()
        moduleHash = dict([(m[1], m[0]) for m in taggedModuleIds])
        taggedConnIds = [(self.uniqueIdConnection(c, moduleHash), c.id)
                         for c in pipeline.connections.itervalues()]
        taggedConnIds.sort()
        hasher = sha.new()
        for t in taggedModuleIds: hasher.update(t[0])
        for t in taggedConnIds: hasher.update(t[0])
        return hasher.digest()

    def uniqueIdModule(self, obj):
        hasher = sha.new()
        hasher.update(obj.name)
        functionsdig = hashList(obj.functions, lambda x: self.uniqueIdFunction(x))
        hasher.update(functionsdig)
        return hasher.digest()

    def uniqueIdConnection(self, con, modHash):
        hasher = sha.new()
        source = modHash[con.sourceId]
        dest = modHash[con.destinationId]
        hasher.update(source)
        hasher.update(dest)
        t = con.type
        if t == VistrailModuleType.Filter:
            hasher.update(str(con.sourcePort))
            hasher.update(str(con.destinationPort))
        elif t == VistrailModuleType.Object:
            hasher.update(con.destinationFunction)
        else:
            raise InvalidVistrailModuleType(t)
        return hasher.digest()

    def uniqueIdFunction(self, f):
        return hashList(f.params, lambda x: self.uniqueIdParam(x))

    def uniqueIdParam(self, p):
        hasher = sha.new()
        hasher.update(p.type)
        hasher.update(p.strValue)
        hasher.update(p.name)
        return hasher.digest()

################################################################################
# Testing

import unittest
from core.vis_types import *
from core.vis_object import *
from core.data_structures import Point
import copy

class TestCache(unittest.TestCase):

    def setUp(self):
        self.c = CacheManager()
        p = ModuleParam()
        p.name = "filename"
        p.type = "string"
        p.strValue = "gkfile.vtk"
        self.p1 = p
        p = ModuleParam()
        p.name = "value"
        p.type = "double"
        p.strValue = "1.0"
        self.p2 = p

    def testEmptyParam(self):
        p = ModuleParam()
        correctDigest = '\xda9\xa3\xee^kK\r2U\xbf\xef\x95`\x18\x90\xaf\xd8\x07\t'
        computedDigest = self.c.uniqueIdParam(p)
        self.assertEqual(correctDigest, computedDigest)

    def testP1(self):
        correctDigest = '?f\xb5\x85hXs\xa8\x0b\xf0q:\xdf\xf2\t\xdc\xeb$f\x91'
        computedDigest = self.c.uniqueIdParam(self.p1)
        self.assertEqual(computedDigest, correctDigest)
        
    def testP2(self):
        correctDigest = 'g\x1f\x0b%\xff\xdf\x01\xdfY\x87z\xaf\xf6\xcf\xe0q\xfb\xd8\xfd]'
        computedDigest = self.c.uniqueIdParam(self.p2)
        self.assertEqual(computedDigest, correctDigest)

    def testF(self):
        f = ModuleFunction()
        f.name = "SetFileName"
        f.returnType = "void"
        f.params = [self.p1, self.p2]
        computedDigest = self.c.uniqueIdFunction(f)
        correctDigest = '\x8b\xc4\x9b\x00\xda\x0bb\xa4/\xbbd\xf8\xb3`I\xe3\xb3*H\xd2'
        self.assertEqual(computedDigest, correctDigest)

    def testParamOrder(self):
        """Parameter order should be irrelevant"""
        import random
        f = ModuleFunction()
        f.name = "SetFileName"
        f.returnType = "void"
        f.params = [self.p1, self.p2]
        digest1 = self.c.uniqueIdFunction(f)
        f.params = [self.p2, self.p1]
        digest2 = self.c.uniqueIdFunction(f)
        self.assertEqual(digest1, digest2)

    def testModule(self):
        m = VisModule()
        m.name = "vtkDataSetReader"
        m.id = 0
        m.cache = 1
        f = ModuleFunction()
        f.name = "SetFileName"
        f.returnType = "void"
        f.params = [self.p1, self.p2]
        m.functions = [f]
        m.center = Point(0, 0)
        correctDigest = '\xe3c@\xb2\x10\x90d\xa5l\x92\x02\x03A\x88\xd7\n\x96\x06\x99q'
        computedDigest = self.c.uniqueIdModule(m)
        self.assertEqual(correctDigest, computedDigest)

    def testFunctionOrder(self):
        """Function order should be irrelevant"""
        m = VisModule()
        m.name = "vtkDataSetReader"
        m.id = 0
        m.cache = 1
        m.center = Point(0, 0)
        f = ModuleFunction()
        f.name = "SetFileName"
        f.returnType = "void"
        f.params = [self.p1, self.p2]
        f2 = copy.copy(f)
        f2.params = [self.p1, self.p1, self.p1, self.p2]
        m.functions = [f, f2]
        digest1 = self.c.uniqueIdModule(m)
        m.functions = [f2, f]
        digest2 = self.c.uniqueIdModule(m)
        self.assertEqual(digest1, digest2)
        
if __name__ == '__main__':
    unittest.main()
    
