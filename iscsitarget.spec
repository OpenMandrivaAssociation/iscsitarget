%define     subrel 2
Name:       iscsitarget
Version:    1.4.20.3
Release:    %mkrel 0
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
#
# other patches
#
Patch1:     iscsitarget-1.4.20.3-dkms.patch
Patch2:	    isciscsitarget-1.4.20.3-makefile.patch
BuildRoot: %{_tmppath}/%{name}-%{version}
BuildRequires: kernel-devel

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
%patch2 -p1 -b .makefile

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


%changelog
* Sat Nov 05 2011 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1.4.20.3-0.2mdv2011.0
+ Revision: 717742
- P1 rediffed
  P2 added
  It compiles now under 2011

* Fri Nov 04 2011 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1.4.20.3-0.1
+ Revision: 717618
- 1.4.20.3

* Fri Nov 04 2011 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1.4.20.2-2
+ Revision: 717386
- spec typo
- 1.4.20.2

  + Luca Berra <bluca@mandriva.org>
    - 2.6.36 compile fix

* Mon Dec 06 2010 Oden Eriksson <oeriksson@mandriva.com> 1.4.20.1-2mdv2011.0
+ Revision: 612419
- the mass rebuild of 2010.1 packages

* Mon Apr 26 2010 Luca Berra <bluca@mandriva.org> 1.4.20.1-1mdv2010.1
+ Revision: 539186
- update to 1.4.20.1
  remove obsolete patches

* Sat Apr 24 2010 Luca Berra <bluca@mandriva.org> 1.4.20-1mdv2010.1
+ Revision: 538445
- new version 1.4.20
- ESX serial number fix from SVN
- remove openssl buildrequire

* Wed Apr 21 2010 Funda Wang <fwang@mandriva.org> 1.4.19-3mdv2010.1
+ Revision: 537333
- rebuild

* Mon Feb 22 2010 Luca Berra <bluca@mandriva.org> 1.4.19-2mdv2010.1
+ Revision: 509454
- new version 1.4.19 + fixes from svn (r293)
  fix strict aliasing
  fix dkms build on 2.6.33 kernels

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild

  + Buchan Milne <bgmilne@mandriva.org>
    - Kernel-compatibility patches for 2.6.28 and up, from google cache of commit list
      for r199, r200,r211,r214 (since berlios.de svn and list archives is missing)
    - r201 and r214 adjusted slightly to try and not break build due to missing r200
    - Adjust makefile to retry patch with -p1 if -p0 failed (new patches need -p1)
    - Build only in usr dir, usr target in toplevel patches kernel which results in
      double patching when dkms builds

* Mon Jan 12 2009 Jérôme Soyer <saispo@mandriva.org> 0.4.17-1mdv2009.1
+ Revision: 328440
- Remove patch because upstream fixed

* Fri Sep 26 2008 Buchan Milne <bgmilne@mandriva.org> 0.4.16-4mdv2009.0
+ Revision: 288569
- Ship patches for older kernels

* Fri Sep 05 2008 Buchan Milne <bgmilne@mandriva.org> 0.4.16-3mdv2009.0
+ Revision: 280999
- Drop kernel-source requires, kernel-devel pulled in by dkms is sufficient

* Thu Sep 04 2008 Buchan Milne <bgmilne@mandriva.org> 0.4.16-2mdv2009.0
+ Revision: 280460
- Fix building the module for a kernel other than the running kernel
- Include header-related fixes required for 2.6.26 and later from svn

* Tue Jun 17 2008 Pascal Terjan <pterjan@mandriva.org> 0.4.16-1mdv2009.0
+ Revision: 223546
- Add the glibc-2.8 patches

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - new version

* Mon Feb 18 2008 Thierry Vignaud <tv@mandriva.org> 0.4.15-4mdv2008.1
+ Revision: 170900
- rebuild
- better summary
- summary is not licence tag
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Tue Oct 02 2007 Olivier Blin <blino@mandriva.org> 0.4.15-3mdv2008.0
+ Revision: 94481
- update to new version

* Sat Jun 02 2007 Stefan van der Eijk <stefan@mandriva.org> 0.4.15-2mdv2008.0
+ Revision: 34749
- add patch for 2.6.22

* Mon Apr 30 2007 Stefan van der Eijk <stefan@mandriva.org> 0.4.15-1mdv2008.0
+ Revision: 19637
- disabled patch0, seems to be merged upstream
- reworked dkms config
- 0.4.15
- add %%version to dkms PACKAGE_VERSION


* Fri Oct 20 2006 Andreas Hasenack <andreas@mandriva.com> 0.4.14-1mdv2007.0
+ Revision: 71437
+ Status: not released
- updated to version 0.4.14
- bump release because the previous (failed) build is still in the queue
- added libopenssl-devel buildrequires
- added dkms package for the iscsi_trgt kernel module
- added initial workings of an init script
- Import iscsitarget

