%global bzr 818


Summary:    MySQL database connector for C++
Name:       mysql-connector-c++
Version:    1.1.0
Release:    0.1.bzr%{?bzr}%{?dist}
Group:      Development/Libraries
License:    GPLv2 with exceptions


URL:        http://forge.mysql.com/wiki/Connector_C++

%if 0%{?bzr}
# bzr branch -r 818 lp:~mysql/mysql-connector-cpp/trunk mysql-connector-c++-1.1.0
# less mysql-connector-c++-1.1.0/driver/mysql_metadata.cpp => getDriverMajorVersion / getDriverMinorVersion / getDriverPatchVersion
# tar czf mysql-connector-c++-bzr818.tgz --exclude .bzr mysql-connector-c++-1.1.0
# rm -rf mysql-connector-c++-1.1.0
Source0:    mysql-connector-c++-bzr%{bzr}.tgz
%else
Source0:    http://dev.mysql.com/get/Downloads/Connector-C++/%{name}-%{version}.tar.gz
%endif

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: cmake mysql-devel boost-devel


%description
MySQL Connector/C++ is a MySQL database connector for C++. 

The MySQL Driver for C++ mimics the JDBC 4.0 API. 
However, Connector/C++ does not implement all of the JDBC 4.0 API.

The Connector/C++ preview features the following classes:
* Connection
* DatabaseMetaData
* Driver
* PreparedStatement
* ResultSet
* ResultSetMetaData
* Savepoint
* Statement 


%package devel
Summary:   MySQL Connector/C++ developer files (headers, examples, etc.)
Group:     Development/Libraries
Requires:  mysql-connector-c++ = %{version}-%{release}
Requires:  mysql-devel

%description devel
These are the files needed to compile programs using MySQL Connector/C++.


%prep
%setup -q

sed -i -e 's/lib$/%{_lib}/' driver/CMakeLists.txt

%{cmake}


%build
%{__make}


%install
%{__rm} -rf %{buildroot}

%{__make} install DESTDIR=%{buildroot}


%check
# for documentation purpose only (A MySQL server is required)
# cd test
# ./static_test tcp://127.0.0.1 user password test_database
# Should output : Loops= 2 Tests=  592 Failures=   0
# ./driver_test tcp://127.0.0.1 user password test_database
# Should output :  Loops= 2 Tests=  592 Failures=   0


%clean
rm -rf %{buildroot} 


%post -p /sbin/ldconfig 

%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc ANNOUNCEMEN* COPYING README CHANGES
%{_libdir}/libmysqlcppconn.so.*
%exclude %{_libdir}/libmysqlcppconn-static.a
#%exclude %{_prefix}/ANNOUNCEMEN*
%exclude %{_prefix}/COPYING
%exclude %{_prefix}/README

%files devel
%defattr(-,root,root,-)
%doc examples/README examples/CMakeLists.txt examples/*.cpp examples/*.h
%{_libdir}/libmysqlcppconn.so
%{_includedir}/mysql*
%{_includedir}/cppconn


%changelog
* Sat Apr 03 2010 Remi Collet <RPMS@famillecollet.com> 1.1.0-0.1.bzr818
- update to 1.1.0 from bzr snapshot 818

* Sat Apr 03 2010 Remi Collet <RPMS@famillecollet.com> 1.0.6-0.1.bzr814
- update to 1.0.6 from bzr snapshot 814

* Sat Jan 23 2010 Remi Collet <RPMS@famillecollet.com> 1.0.6-0.1.bzr813
- update to 1.0.6 from bzr snapshot 813

* Sun Jan 10 2010 Remi Collet <RPMS@famillecollet.com> 1.0.6-0.1.bzr812
- update to 1.0.6 from bzr snapshot

* Tue Nov 24 2009 Remi Collet <RPMS@famillecollet.com> 1.0.5-1.1
- rebuild

* Sun Jun 28 2009 Remi Collet <RPMS@famillecollet.com> 1.0.5-1
- initial RPM

