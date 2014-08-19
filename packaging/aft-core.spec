#
# Copyright (c) 2013-14 Intel, Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; version 2 of the License
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.

%define projectname aft

Name:       %{projectname}-core
Summary:    Automated Flasher and Tester for OS SW images
Version:    0.0.0
Release:    1
Group:      Development/Tools
License:    GPL-2.0+
BuildArch:  noarch
Source:     %{name}-%{version}.tar.gz

BuildRequires: python
BuildRequires: python-setuptools
BuildRequires: fdupes

Requires: python-setuptools

%description
Tool for performing automated flashing and testing of OS SW images.

%prep
%setup -q

%build
%{__python} setup.py build


%install
rm -rf %{buildroot}
%{__python} setup.py install -O2 --root=%{buildroot} --prefix=%{_prefix}
%fdupes %{buildroot}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{python_sitelib}/%{projectname}-%{version}-*.egg-info
%{python_sitelib}/%{projectname}
%{_datadir}/%{projectname}

%changelog
