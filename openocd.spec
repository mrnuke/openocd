Name:       openocd
Version:    0.10.0
Release:    2%{?dist}
Summary:    Debugging, in-system programming and boundary-scan testing for embedded devices

Group:      Development/Tools
License:    GPLv2
URL:        https://github.com/mrnuke/openocd
Source0:    %{version}/%{name}-%{version}.tar.gz

BuildRequires:  chrpath, libftdi-devel, libusbx-devel, jimtcl-devel, hidapi-devel, sdcc, libusb-devel, texinfo
BuildRequires: libtool autoconf automake
Requires(post): info
Requires(preun):info

%description
The Open On-Chip Debugger (OpenOCD) provides debugging, in-system programming
and boundary-scan testing for embedded devices. Various different boards,
targets, and interfaces are supported to ease development time.

Install OpenOCD if you are looking for an open source solution for hardware
debugging.

%prep
%setup -q
rm -f src/jtag/drivers/OpenULINK/ulink_firmware.hex

%build
# See bootstrap.sh for instructions
aclocal
libtoolize
autoconf
autoheader
automake --add-missing

pushd src/jtag/drivers/OpenULINK
make PREFIX=sdcc hex
popd

# J-Link support code is now part of libjaylink. Until libjaylink becomes a
# Fedora package, we have to disable J-Link programmers.
%configure \
  --disable-werror \
  --enable-static \
  --disable-shared \
  --enable-dummy \
  --enable-ftdi \
  --enable-stlink \
  --enable-ti-icdi \
  --enable-ulink \
  --enable-usb-blaster-2 \
  --disable-jlink \
  --enable-osbdm \
  --enable-opendous \
  --enable-aice \
  --enable-vsllink \
  --enable-usbprog \
  --enable-rlink \
  --enable-armjtagew \
  --enable-cmsis-dap \
  --enable-parport \
  --enable-parport_ppdev \
  --enable-jtag_vpi \
  --enable-usb_blaster_libftdi \
  --enable-amtjtagaccel \
  --enable-ep39xx \
  --enable-at91rm9200 \
  --enable-gw16012 \
  --enable-presto_libftdi \
  --enable-openjtag_ftdi \
  --enable-buspirate \
  --enable-sysfsgpio \
  --enable-remote-bitbang \
  --disable-internal-jimtcl \
  --disable-internal-libjaylink \
  --disable-doxygen-html \
  CROSS=
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot} INSTALL="install -p"
rm -f %{buildroot}/%{_infodir}/dir
rm -f %{buildroot}/%{_libdir}/libopenocd.*
rm -rf %{buildroot}/%{_datadir}/%{name}/contrib
mkdir -p %{buildroot}/%{_prefix}/lib/udev/rules.d/
install -p -m 644 contrib/60-openocd.rules %{buildroot}/%{_prefix}/lib/udev/rules.d/69-openocd.rules
sed -i 's/MODE="664", GROUP="plugdev"/TAG+="uaccess"/' %{buildroot}/%{_prefix}/lib/udev/rules.d/69-openocd.rules
chrpath --delete %{buildroot}/%{_bindir}/openocd

%post
/sbin/install-info %{_infodir}/%{name}.info.gz %{_infodir}/dir || :

%preun
if [ $1 = 0 ]; then
    /sbin/install-info --delete %{_infodir}/%{name}.info.gz %{_infodir}/dir || :
fi

%files
%doc README COPYING AUTHORS ChangeLog NEWS TODO
%{_datadir}/%{name}/scripts
%{_datadir}/%{name}/OpenULINK/ulink_firmware.hex
%{_bindir}/%{name}
%{_prefix}/lib/udev/rules.d/69-openocd.rules
# doc
%{_infodir}/%{name}.info*.gz
%{_mandir}/man1/*

%changelog
* Mon Feb 27 2017 Alexandru Gagniuc <mr.nuke.me@gmail.com> - 0.10.0-2
- Merge ARC branch into openocd sources
- Use github branch for SCM since most of this is unmerged

* Mon Feb 27 2017 Alexandru Gagniuc <mr.nuke.me@gmail.com> - 0.10.0-1
- Update to openocd 0.10.0

* Mon Feb 27 2017 Alexandru Gagniuc <mr.nuke.me@gmail.com> - 0.9.0-6
- Use 'PREFIX' make variable instead of patching makefile

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri May 13 2016 Markus Mayer <lotharlutz@gmx.de> - 0.9.0-4
- Fix wrong udev rules bz#1177996

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon May 18 2015 Jiri Kastner <jkastner@redhat.com> - 0.9.0-1
- update to 0.9.0
- added texinfo dependency
