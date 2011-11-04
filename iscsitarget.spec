Name:       iscsitarget
Version:    1.4.20.2
Release:    %mkrel 2
Summary:    iSCSI target
License:    GPL
Group:      Networking/Other
URL:        http://iscsitarget.sourceforge.net/
Source0:    http://downloads.sourceforge.net/iscsitarget/%{name}-%{version}.tar.gz
Source1:    iscsitarget.init
Source2:    iscitarget-2.6.22.patch
#
# patches from svn
# for i in $(seq 330 331);do
# svn log -c $i http://iscsitarget.svn.sourceforge.net/svnroot/iscsitarget/trunk > iscsitarget-r$i.patch
# svn diff -c $i http://iscsitarget.svn.sourceforge.net/svnroot/iscsitarget/trunk >> iscsitarget-r$i.patch
# done
#
Patch373:	iscsitarget-r373.patch
#
# other patches
#
Patch1:     iscsitarget-1.4.20-dkms.patch
BuildRoot: %{_tmppath}/%{name}-%{version}

%define dkmsdir %{_usrsrc}/%{name}-%{version}-%{release}

%description
iSCSI Enterprise Target is for building an iSCSI storage system on
Linux. It is aimed at developing an iSCSI target satisfying enterprise
requirements.

%package -n dkms-%{name}
Summary: iSCSI-target kernel module
Group: Networking/Other
Requires(preun): dkms
Requires(post): dkms

%description -n dkms-%{name}
This package contains the iscsi-target kernel module.

%prep
%setup -q

cp %{SOURCE2} patches/compat-mdv2008.patch
%patch1 -p1 -b .dkms.orig
%patch373 -p0 -b .r373.orig

%build
%make -C usr CC="gcc %optflags %{?ldflags:%ldflags}"

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} KVER=`uname -r` install-usr install-man

# do this manually to install in proper paths
mkdir -p %{buildroot}%{_initrddir}
install %{SOURCE1} %{buildroot}%{_initrddir}/iscsi-target
cp etc/ietd.conf %{buildroot}%{_sysconfdir}
cp etc/*.allow %{buildroot}%{_sysconfdir}

# DKMS
mkdir -p %{buildroot}%{dkmsdir}
cp -r kernel include patches %{buildroot}%{dkmsdir}/
# remove patch backup files
rm -f  %{buildroot}%{dkmsdir}/*/*.r*.orig

sed -e 's@^PACKAGE_VERSION=.*$@PACKAGE_VERSION="%{version}-%{release}"@' dkms.conf > %{buildroot}%{dkmsdir}/dkms.conf

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
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc ChangeLog COPYING README* RELEASE_NOTES
%config(noreplace) %{_sysconfdir}/ietd.conf
%config(noreplace) %{_sysconfdir}/initiators.allow
%config(noreplace) %{_sysconfdir}/targets.allow
%{_initrddir}/iscsi-target
%{_sbindir}/ietadm
%{_sbindir}/ietd
%{_mandir}/man5/ietd.conf.5*
%{_mandir}/man8/ietd.8*
%{_mandir}/man8/ietadm.8*

%files -n dkms-%{name}
%defattr(-,root,root)
%{_usrsrc}/%{name}-%{version}-%{release}

