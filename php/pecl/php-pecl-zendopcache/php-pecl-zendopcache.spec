# spec file for php-pecl-zendopcache
#
# Copyright (c) 2013 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Please, preserve the changelog entries
#
%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}
%global proj_name  ZendOpcache
%global pecl_name  zendopcache
%global plug_name  opcache

Name:          php-pecl-%{pecl_name}
Version:       7.0.2
Release:       1%{?dist}
Summary:       The Zend OPcache

Group:         Development/Libraries
License:       PHP
URL:           http://pecl.php.net/package/%{proj_name}
Source0:       http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
# this extension must be loaded before XDebug
# So "opcache" if before "xdebug"
Source1:       %{plug_name}.ini
Source2:       %{plug_name}-default.blacklist

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: php-devel >= 5.2.0
BuildRequires: php-pear

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Requires:      php(zend-abi) = %{php_zend_api}
Requires:      php(api) = %{php_core_api}

# Only one opcode cache could be enabled
Conflicts:     php-eaccelerator
Conflicts:     php-xcache
# APC 3.1.15 offer an option to disable opcache
Conflicts:     php-pecl-apc < 3.1.15
Provides:      php-pecl(%{plug_name}) = %{version}%{?prever}
Provides:      php-pecl(%{plug_name})%{?_isa} = %{version}%{?prever}
Provides:      php-%{plug_name} = %{version}-%{release}
Provides:      php-%{plug_name}%{?_isa} = %{version}-%{release}
Obsoletes:     php-pecl-zendoptimizerplus < %{version}-%{release}
Provides:      php-pecl-zendoptimizerplus = %{version}-%{release}
Provides:      php-pecl-zendoptimizerplus%{?_isa} = %{version}-%{release}

# Filter private shared
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}


%description
The Zend OPcache provides faster PHP execution through opcode caching and
optimization. It improves PHP performance by storing precompiled script
bytecode in the shared memory. This eliminates the stages of reading code from
the disk and compiling it on future access. In addition, it applies a few
bytecode optimization patterns that make code execution faster.


%prep
%setup -q -c
mv %{pecl_name}-%{version} NTS

cd NTS

# Sanity check, really often broken
extver=$(sed -n '/#define ACCELERATOR_VERSION/{s/.* "//;s/".*$//;p}' ZendAccelerator.h)
if test "x${extver}" != "x%{version}%{?prever:-%{prever}}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?prever:-%{prever}}.
   exit 1
fi
cd ..

# Duplicate source tree for NTS / ZTS build
cp -pr NTS ZTS


%build
cd NTS
%{_bindir}/phpize
%configure \
    --enable-optimizer-plus \
    --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}

cd ../ZTS
%{_bindir}/zts-phpize
%configure \
    --enable-optimizer-plus \
    --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}


%install
rm -rf %{buildroot}

install -D -p -m 644 %{SOURCE1} %{buildroot}%{php_inidir}/%{plug_name}.ini
sed -e 's:@EXTPATH@:%{php_extdir}:' \
    -i %{buildroot}%{php_inidir}/%{plug_name}.ini

make -C NTS install INSTALL_ROOT=%{buildroot}

install -D -p -m 644 %{SOURCE1} %{buildroot}%{php_ztsinidir}/%{plug_name}.ini
sed -e 's:@EXTPATH@:%{php_ztsextdir}:' \
    -i %{buildroot}%{php_ztsinidir}/%{plug_name}.ini

make -C ZTS install INSTALL_ROOT=%{buildroot}

# The default Zend OPcache blacklist file
install -D -p -m 644 %{SOURCE2} %{buildroot}%{php_inidir}/%{plug_name}-default.blacklist

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml


%clean
rm -rf %{buildroot}


%check
cd NTS
%{__php} \
    -n -d zend_extension=%{buildroot}%{php_extdir}/%{plug_name}.so \
    -m | grep "Zend OPcache"

TEST_PHP_EXECUTABLE=%{__php} \
TEST_PHP_ARGS="-n -d zend_extension=%{buildroot}%{php_extdir}/%{plug_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__php} -n run-tests.php

cd ../ZTS
%{__ztsphp} \
    -n -d zend_extension=%{buildroot}%{php_ztsextdir}/%{plug_name}.so \
    -m | grep "Zend OPcache"

TEST_PHP_EXECUTABLE=%{__ztsphp} \
TEST_PHP_ARGS="-n -d zend_extension=%{buildroot}%{php_ztsextdir}/%{plug_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__ztsphp} -n run-tests.php


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%defattr(-,root,root,-)
%doc NTS/{LICENSE,README}
%config(noreplace) %{php_inidir}/%{plug_name}-default.blacklist
%config(noreplace) %{php_inidir}/%{plug_name}.ini
%{php_extdir}/%{plug_name}.so

%config(noreplace) %{php_ztsinidir}/%{plug_name}.ini
%{php_ztsextdir}/%{plug_name}.so

%{pecl_xmldir}/%{name}.xml


%changelog
* Wed Jun  5 2013 Remi Collet <rcollet@redhat.com> - 7.0.2-1
- update to 7.0.2
- add spec License = CC-BY-SA

* Thu Apr 11 2013 Remi Collet <rcollet@redhat.com> - 7.0.1-2
- allow wildcard in opcache.blacklist_filename and provide
  default /etc/php.d/opcache-default.blacklist

* Mon Mar 25 2013 Remi Collet <remi@fedoraproject.org> - 7.0.1-1
- official PECL release, version 7.0.1 (beta)
- rename to php-pecl-zendopcache

* Mon Mar 18 2013 Remi Collet <remi@fedoraproject.org> - 7.0.1-0.1.gitcef6093
- update to git snapshot, with new name (opcache)

* Sun Mar 10 2013 Remi Collet <remi@fedoraproject.org> - 7.0.0-2
- allow to install with APC >= 3.1.15 (user data cache)

* Tue Mar  5 2013 Remi Collet <remi@fedoraproject.org> - 7.0.0-1
- official PECL release, version 7.0.0 (beta)

* Thu Feb 28 2013 Remi Collet <remi@fedoraproject.org> - 7.0.0-0.7.gitd39a49a
- new snapshot
- run test suite during build

* Thu Feb 21 2013 Remi Collet <remi@fedoraproject.org> - 7.0.0-0.6.git3a06991
- new snapshot

* Fri Feb 15 2013 Remi Collet <remi@fedoraproject.org> - 7.0.0-0.4.git2b6eede
- new snapshot (ZTS fixes)

* Thu Feb 14 2013 Remi Collet <remi@fedoraproject.org> - 7.0.0-0.2.gitafb43f5
- new snapshot
- better default configuration file (new upstream recommendation)
- License file now provided by upstream

* Wed Feb 13 2013 Remi Collet <remi@fedoraproject.org> - 7.0.0-0.1.gitaafc145
- initial package
