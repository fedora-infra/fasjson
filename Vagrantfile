# -*- mode: ruby -*-
# vi: set ft=ruby :

ENV['VAGRANT_NO_PARALLEL'] = 'yes'

Vagrant.configure(2) do |config|
  config.hostmanager.enabled = true
  config.hostmanager.manage_host = true
  config.hostmanager.manage_guest = true

  config.vm.define "fasjson" do |fasjson|
    fasjson.vm.box_url = "https://download.fedoraproject.org/pub/fedora/linux/releases/38/Cloud/x86_64/images/Fedora-Cloud-Base-Vagrant-38-1.6.x86_64.vagrant-libvirt.box"
    fasjson.vm.box = "f38-cloud-libvirt"
    fasjson.vm.hostname = "fasjson-dev.tinystage.test"

    fasjson.vm.synced_folder ".", "/vagrant", disabled: true
    fasjson.vm.synced_folder ".", "/home/vagrant/fasjson", type: "sshfs"

    fasjson.vm.provider :libvirt do |libvirt|
      libvirt.cpus = 2
      libvirt.memory = 2048
    end

    fasjson.vm.provision "ansible" do |ansible|
      ansible.playbook = "devel/ansible/fasjson.yml"
      ansible.verbose = true
    end
  end
end
