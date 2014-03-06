%define dkmsdir %{_usrsrc}/%{name}-%{version}-%{release}

Summary:	iSCSI target
Name:		iscsitarget
Version:	1.4.20.3
Release:	1
License:	GPLv2+
Group:		Networking/Other
Url:		http://iscsitarget.sourceforge.net/
Source0:	http://downloads.sourceforge.net/iscsitarget/%{name}-%{version}.tar.gz
Source1:	iscsitarget.init
Source2:	iscitarget-2.6.22.patch
Source10:	%{name}.rpmlintrc
Patch1:		iscsitarget-1.4.20.3-dkms.patch
Patch2:		isciscsitarget-1.4.20.3-makefile.patch
BuildRequires:	kernel-devel

%description
iSCSI Enterprise Target is for building an iSCSI storage system on
Linux. It is aimed at developing an iSCSI target satisfying enterprise
requirements.

%files
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

%preun
%_preun_service iscsi-target

%post
%_post_service iscsi-target

#----------------------------------------------------------------------------

%package -n dkms-%{name}
Summary:	iSCSI-target kernel module
Group:		Networking/Other
Requires(preun,post):	dkms

%description -n dkms-%{name}
This package contains the iscsi-target kernel module.

%files -n dkms-%{name}
%{_usrsrc}/%{name}-%{version}-%{release}

%preun -n dkms-%{name}
dkms remove -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --all || :

%post -n dkms-%{name}
dkms add -m %{name} -v %{version}-%{release} --rpm_safe_upgrade
dkms build -m %{name} -v %{version}-%{release} --rpm_safe_upgrade
dkms install -m %{name} -v %{version}-%{release} --rpm_safe_upgrade

#----------------------------------------------------------------------------

%prep
%setup -q
cp %{SOURCE2} patches/compat-mdv2008.patch
%patch1 -p1 -b .dkms.orig
%patch2 -p1 -b .makefile

find . -name .svn | xargs rm -rf

%build
%make -C usr CC="gcc %{optflags} %{ldflags}"

%install
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

