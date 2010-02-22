Name:       iscsitarget
Version:    1.4.19
Release:    %mkrel 2
Summary:    iSCSI target
License:    GPL
Group:      Networking/Other
URL:        http://iscsitarget.sourceforge.net/
Source0:    http://downloads.sourceforge.net/iscsitarget/%{name}-%{version}.tar.gz
Source1:    iscsitarget.init
Source2:    iscitarget-2.6.22.patch
Source3:    iscitarget-2.6.33.patch
#
# patches from svn
# for i in $(seq 277 293);do
# svn log -c $i http://iscsitarget.svn.sourceforge.net/svnroot/iscsitarget/trunk > iscsitarget-r$i.patch
# svn diff -c $i http://iscsitarget.svn.sourceforge.net/svnroot/iscsitarget/trunk >> iscsitarget-r$i.patch
# done
#
Patch277: iscsitarget-r277.patch
Patch278: iscsitarget-r278.patch
Patch279: iscsitarget-r279.patch
Patch280: iscsitarget-r280.patch
Patch281: iscsitarget-r281.patch
Patch282: iscsitarget-r282.patch
Patch285: iscsitarget-r285.patch
Patch288: iscsitarget-r288.patch
Patch289: iscsitarget-r289.patch
Patch290: iscsitarget-r290.patch
Patch291: iscsitarget-r291.patch
Patch292: iscsitarget-r292.patch
Patch293: iscsitarget-r293.patch
#
# other patches
#
Patch0:     iscsitarget-1.4.19-strict-alias.patch
Patch1:     iscsitarget-1.4.19-dkms.patch
BuildRequires: libopenssl-devel
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
%patch277 -p0 -b .r277
%patch278 -p0 -b .r278
%patch279 -p0 -b .r279
%patch280 -p0 -b .r280
%patch281 -p0 -b .r281
%patch282 -p0 -b .r282
%patch285 -p0 -b .r285
%patch288 -p0 -b .r288
%patch289 -p0 -b .r289
%patch290 -p0 -b .r290
%patch291 -p0 -b .r291
%patch292 -p0 -b .r292
%patch293 -p0 -b .r293

cp %{SOURCE2} patches/
cp %{SOURCE3} patches/
%patch0 -p1 -b .alias
%patch1 -p1 -b .dkms

%build
%make -C usr CC="gcc %optflags %{?ldflags:%ldflags}"

%install
rm -rf %{buildroot}
make DISTDIR=%{buildroot} KVER=`uname -r` install-usr install-man

# do this manually to install in proper paths
mkdir -p %{buildroot}%{_initrddir}
install %{SOURCE1} %{buildroot}%{_initrddir}/iscsi-target
cp etc/ietd.conf %{buildroot}%{_sysconfdir}
cp etc/*.allow %{buildroot}%{_sysconfdir}

# DKMS
mkdir -p %{buildroot}%{dkmsdir}
cp -r kernel include patches %{buildroot}%{dkmsdir}/

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

