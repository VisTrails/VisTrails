# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.define "x86", primary: true do |m|
    m.vm.box = "hashicorp/precise32"
  end
  config.vm.define "x86_64", autostart: false do |m|
    m.vm.box = "hashicorp/precise64"
  end

  config.vm.provision "shell",
    inline: <<SCRIPT
sudo aptitude update -y
sudo aptitude install -y python python-dateutil python-dev python-docutils \
    python-mako python-matplotlib python-mysqldb python-numpy python-paramiko \
    python-pip python-qt4 python-qt4-gl python-qt4-sql python-scipy \
    python-setuptools python-sphinx python-sqlalchemy python-suds python-tz \
    python-unittest2 python-virtualenv python-vtk python-xlrd python-xlwt \
    zip unzip xvfb
cd /home/vagrant
virtualenv --system-site-packages venv
source venv/bin/activate
cd /vagrant
pip install -r requirements.txt
python setup.py develop
sudo chown -R vagrant:vagrant /home/vagrant/venv
SCRIPT
end
