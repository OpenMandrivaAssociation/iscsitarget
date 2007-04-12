%define module_name dkms-iscsitarget

Name: iscsitarget
Summary: Open source iSCSI target
Version: 0.4.14
Release: %mkrel 1
License: GPL
Group: Networking/Other
Source0: iscsitarget-%{version}.tar.gz
Source1: iscsitarget.init
Patch: iscsitarget-install.patch
BuildRequires: libopenssl-devel
URL: http://iscsitarget.sourceforge.net/
BuildRoot: %{_tmppath}/%{name}-%{version}-root-%(id -u -n)

%description
iSCSI Enterprise Target is for building an iSCSI storage system on
Linux. It is aimed at developing an iSCSI target satisfying enterprise
requirements.

%package -n %{module_name}
Summary: iscsi-target kernel module
Group: Networking/Other
Requires: kernel-source
Requires(preun): dkms
Requires(post): dkms

%description -n %{module_name}
This package contains the iscsi-target kernel module.

%prep
%setup -q
%patch -p1 -b .install

%build
%make progs

%install
rm -rf $RPM_BUILD_ROOT
make DISTDIR=%{buildroot} progs_install

mkdir -p %{buildroot}%{_mandir}/man{5,8}
install -m 0644 doc/manpages/ietd.8 %{buildroot}%{_mandir}/man8/
install -m 0644 doc/manpages/ietd.conf.5 %{buildroot}%{_mandir}/man5/

mkdir -p %{buildroot}%{_initrddir}
mv -f %{buildroot}%{_sysconfdir}/init.d/iscsi-target %{buildroot}%{_initrddir}

# conf
install -m 0644 etc/ietd.conf %{buildroot}%{_sysconfdir}
install -m 0644 etc/initiators.allow %{buildroot}%{_sysconfdir}
install -m 0644 etc/initiators.deny %{buildroot}%{_sysconfdir}

# init script
mkdir -p %{buildroot}%{_initrddir}
install -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/iscsi-target

# DKMS
mkdir -p %{buildroot}/usr/src/%{module_name}-%{version}
mkdir -p %{buildroot}/usr/src/%{module_name}-%{version}/usr
cp -a kernel %{buildroot}/usr/src/%{module_name}-%{version}
cp -a include %{buildroot}/usr/src/%{module_name}-%{version}
cp -f Makefile %{buildroot}/usr/src/%{module_name}-%{version}
cp usr/Makefile %{buildroot}/usr/src/%{module_name}-%{version}/usr

cat > %{buildroot}/usr/src/%{module_name}-%{version}/dkms.conf <<EOF
PACKAGE_VERSION="%{version}"
PACKAGE_NAME="%{module_name}"
MAKE[0]="cd \${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build ; make mods"
CLEAN="cd \${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build ; make clean"

BUILT_MODULE_NAME[0]="iscsi_trgt"
BUILT_MODULE_LOCATION[0]="kernel"
DEST_MODULE_NAME[0]="iscsi_trgt"
DEST_MODULE_LOCATION[0]="/kernel/iscsi"

REMAKE_INITRD="no"
AUTOINSTALL=yes
POST_INSTALL="post-install"
POST_REMOVE="post-remove"
EOF

%post -n %{module_name}
dkms add -m %{module_name} -v %{version} --rpm_safe_upgrade
dkms build -m %{module_name} -v %{version} --rpm_safe_upgrade
dkms install -m %{module_name} -v %{version} --rpm_safe_upgrade

%post
%_post_service iscsi-target

%preun -n %{module_name}
dkms remove -m %{module_name} -v %{version} --rpm_safe_upgrade --all || :

%preun
%_preun_service iscsi-target

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc ChangeLog COPYING README
%config(noreplace) %{_sysconfdir}/ietd.conf
%config(noreplace) %{_sysconfdir}/initiators.allow
%config(noreplace) %{_sysconfdir}/initiators.deny
%{_initrddir}/iscsi-target
%{_sbindir}/ietadm
%{_sbindir}/ietd
%{_mandir}/man5/ietd.conf.5*
%{_mandir}/man8/ietd.8*

%files -n %{module_name}
%defattr(-,root,root)
%_usrsrc/%{module_name}-%{version}



