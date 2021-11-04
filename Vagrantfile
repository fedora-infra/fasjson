# -*- mode: ruby -*-
# vi: set ft=ruby :

ENV['VAGRANT_NO_PARALLEL'] = 'yes'

Vagrant.configure(2) do |config| 
  config.hostmanager.enabled = true
  config.hostmanager.manage_host = true
  config.hostmanager.manage_guest = true

  config.vm.define "freeipa" do |freeipa|
    freeipa.vm.box_url = "https://download.fedoraproject.org/pub/fedora/linux/releases/34/Cloud/x86_64/images/Fedora-Cloud-Base-Vagrant-34-1.2.x86_64.vagrant-libvirt.box"
    freeipa.vm.box = "f34-cloud-libvirt"
    freeipa.vm.hostname = "ipa.example.test"
    freeipa.hostmanager.aliases = ("kerberos.example.test")
    
    freeipa.vm.provider :libvirt do |libvirt|
      libvirt.cpus = 2
      libvirt.memory = 2048 
    end
    
    # Vagrant adds '127.0.0.1 ipa.example.test ipa' as the first line in /etc/hosts
    # and freeipa doesnt like that, so we remove it
    freeipa.vm.provision "shell", inline: "sudo sed -i '1d' /etc/hosts"

    freeipa.vm.provision "ansible" do |ansible|
      ansible.playbook = "devel/ansible/freeipa.yml"
    end
  end
  
  config.vm.define "fasjson" do |fasjson|
    fasjson.vm.box_url = "https://download.fedoraproject.org/pub/fedora/linux/releases/34/Cloud/x86_64/images/Fedora-Cloud-Base-Vagrant-34-1.2.x86_64.vagrant-libvirt.box"
    fasjson.vm.box = "f34-cloud-libvirt"
    fasjson.vm.hostname = "fasjson.example.test"
    
    fasjson.vm.synced_folder ".", "/vagrant/", type: "sshfs"

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
