# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box_url = "https://download.fedoraproject.org/pub/fedora/linux/releases/31/Cloud/x86_64/images/Fedora-Cloud-Base-Vagrant-31-1.9.x86_64.vagrant-libvirt.box"
  config.vm.box = "f31-cloud-libvirt"
  config.vm.define "fasjson"
  config.vm.synced_folder ".", "/vagrant/", type: "sshfs"
  config.vm.hostname = "ipa.example.test"
  config.hostmanager.enabled = true
  config.hostmanager.manage_host = true
  config.vm.provider :libvirt do |libvirt|
    libvirt.cpus = 2
    libvirt.memory = 2048 
  end

  # Vagrant adds '127.0.0.1 ipa.example.test ipa' as the first line in /etc/hosts
  # and freeipa doesnt like that, so we remove it
  config.vm.provision "shell", inline: "sudo sed -i '1d' /etc/hosts"

  # We need to use old cgroups as freeipa will not work at all with v2
  config.vm.provision "shell", inline: "grubby --update-kernel=ALL --args='systemd.unified_cgroup_hierarchy=0'"

  # We need to reload the box mid-provision. This is to allow us to run a docker container on the above v1 cgroups
  config.vm.provision :reload

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/playbook.yml"
  end

end
