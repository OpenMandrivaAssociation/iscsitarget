Name: iscsitarget
Summary: Open source iSCSI target
Version: 0.4.15
Release: %mkrel 1
License: GPL
Group: Networking/Other
Source0: iscsitarget-%{version}.tar.bz2
Source1: iscsitarget.init
Patch: iscsitarget-install.patch
BuildRequires: libopenssl-devel
URL: http://iscsitarget.sourceforge.net/
BuildRoot: %{_tmppath}/%{name}-%{version}-root-%(id -u -n)

%description
iSCSI Enterprise Target is for building an iSCSI storage system on
Linux. It is aimed at developing an iSCSI target satisfying enterprise
requirements.

%package -n dkms-%{name}
Summary: iscsi-target kernel module
Group: Networking/Other
Requires: kernel-source
Requires(preun): dkms
Requires(post): dkms

%description -n dkms-%{name}
This package contains the iscsi-target kernel module.

%prep
%setup -q
#patch -p1 -b .install

%build
%make usr

%install
rm -rf $RPM_BUILD_ROOT
make DISTDIR=%{buildroot} install-etc install-usr

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
mkdir -p %{buildroot}/usr/src/%{name}-%{version}-%{release}
mkdir -p %{buildroot}/usr/src/%{name}-%{version}-%{release}/usr
cp -a kernel %{buildroot}/usr/src/%{name}-%{version}-%{release}
cp -a include %{buildroot}/usr/src/%{name}-%{version}-%{release}
cp -f Makefile %{buildroot}/usr/src/%{name}-%{version}-%{release}
cp usr/Makefile %{buildroot}/usr/src/%{name}-%{version}-%{release}/usr

cat > %{buildroot}/usr/src/%{name}-%{version}-%{release}/dkms.conf <<EOF
PACKAGE_VERSION="%{version}-%{release}"
PACKAGE_NAME="%{name}"
MAKE[0]="cd \${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build ; make kernel"
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

%post -n dkms-%{name}
dkms add -m %{name} -v %{version}-%{release} --rpm_safe_upgrade
dkms build -m %{name} -v %{version}-%{release} --rpm_safe_upgrade
dkms install -m %{name} -v %{version}-%{release} --rpm_safe_upgrade

%post
%_post_service iscsi-target

%preun -n dkms-%{name}
dkms remove -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --all || :

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

%files -n dkms-%{name}
%defattr(-,root,root)
%_usrsrc/%{name}-%{version}-%{release}



