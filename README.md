# Base OS Setup Role

Author: Brad House<br/>
License: MIT<br/>
Original Repository: https://github.com/bradh352/ansible-role-base-linux

## Overview

This role is used to configure a Linux host with some minimum requirements 
common to all systems, including hardening as per CIS and PCI-DSS standards.

## Variables used by this role

- `superuser` - Name of the superuser to ensure exists on a system. Required.
- `superuser_password` - Password for the superuser.  Should be stored in a
  vault. Required.
- `superuser_pubkey` - list of SSH public keys to associated with the superuser
  account. Optional.
- `timezone` - Validate timezone such as `America/New_York`, `US/Eastern`, or `UTC`
  as can be seen as paths in `/usr/share/zoneinfo/`. Defaults to `UTC`.
- `admin_email` - Email address to use for notifications, such as cron task
  failures. Required.
- `smtp_server` - SMTP server to use to send emails through. Required.
- `ssh_port` - Port to listen for inbound SSH connections. Defaults to 22.
- `ssh_password_auth` - Whether or not to allow password authentication.
  Default `false`.  Recommended to use SSH public keys or GSSAPI.
- `os_autoupdate` - Whether to allow the OS to perform automatic updates.
  Defaults to `false`.
- `skip_updates` - This role automatically attempts to upgrade all packages to
  their latest versions.  May specify `-e skip_updates=true` on the command line
  to bypass this behavior.
- `cpu_governor` - The CPU governor to use.  Only relevant for physical hosts.
  Defaults to `performance` if not provided.
- `lsi_reset_workaround` - If an LSI controller is found with SATA SSDs attached
  set the queue depth to `1` (effectively disabling NCQ) to workaround a known
  disk reset issue.  Default `true`.  Even when true, only sets the queue depth
  when the specified combination is found.
- `disable_hwe` - By default for ubuntu LTS systems, will install the Hardware
  Enablement kernel. Set this to `true` to use the kernel that shipped with the
  release.
- `ntp_pools` - List of NTP pools. Defaults to
  `["0.us.pool.ntp.org", "1.us.pool.ntp.org", "2.us.pool.ntp.org", "3.us.pool.ntp.org"]`
- `ntp_peers` - If running multiple internal NTP servers, these can be the ones to
  peer with. Default none.  When setting this configuration it also allows
  connections from anywhere.
- `host_use_default_ip` - In the `/etc/hosts` file the hostname of the machine
  is registered by default using `127.0.1.1` as the address.  This is good for
  machines where the IP address may change (e.g. DHCP).  However some services
  may require static addressing and validate the machine's hostname matches a
  non-local ip address (such as FreeIPA server), when set to `true`, it will use
  the ip address of the network interface that has a default route.  Default
  `false`.
- `base_additional_hosts` - Add list of additional hosts to `/etc/hosts`.  This
  can be used for handling situations where DNS may be offline for critical
  neighbors. Each item in the list must contain an `ip` and `host` entry.
  E.g. `[ { "ip": "192.168.1.5", "host": "blue" }, ... ]`
- `grub_password` - This is a hashed password used by Grub for making changes
  via the grub menu.  It must be generated via:
  `grub2-mkpasswd-pbkdf2` (RedHat) or `grub-mkpasswd-pbkdf2` (Debian)
  We can't do this dynamically because of the random salt, so it is no longer
  idempotent.  So we cache it here.  Should be updated whenever
  `superuser_password` is updated if using the same password.  Likely this should
  also be stored in the vault even though it is hashed.
- `mirror_rocky`: URL prefix for rocky linux mirror.  Optional.
  E.g. `https://plug-mirror.rcac.purdue.edu/rocky`
- `mirror_epel`: URL prefix for EPEL mirror.  Optional.  E.g.
  `https://mirror.nodesdirect.com/epel`
- `mirror_debian`: URL prefix for Debian Linux mirror.  Optional.
   E.g. `https://mirror.nodesdirect.com/debian`
- `mirror_ubuntu`: URL prefix for Ubuntu Linux mirror.  Optional.
   E.g. `https://mirror.nodesdirect.com/ubuntu`

## Initial deployment

Since the username and password used to log into a machine may not be the same
as gets used once this playbook runs, these additional command line
`ansible-playbook` variables may need to be specified:
```
-e ansible_user=infra -e ansible_password="Test123$" -e ansible_become_password="Test123$"
```
 * NOTE: do not use `ansible_become_pass` as that isn't able to be overwriten
   internally by the playbook as part of the process of changing authentication
   during the deployment.
