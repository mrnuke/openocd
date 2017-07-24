Name:       openocd
Version:    0.10.1
Release:    1%{?dist}
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
* Mon Jul 24 2017 Alexandru Gagniuc <alex.g@adaptrum.com> 0.10.1-1
- Build with tito (mr.nuke.me@gmail.com)
- Initialized to use tito. (mr.nuke.me@gmail.com)
- flash/nor: Add support for Anarion QSPI controller (alex.g@adaptrum.com)
- arc: Flush L2 cache at reset for ARC HS (Anton.Kolesov@synopsys.com)
- ARC: Check size of actionpoints_list in arc_dbg_set_watchpoint()
  (mr.nuke.me@gmail.com)
- ARC: Check size of arc32->actionpoints_list before dereferencing
  (mr.nuke.me@gmail.com)
- ARC: arc_mntr.c: Constify string parameters to Jim_GetOpt_String()
  (mr.nuke.me@gmail.com)
- ARC: Update signature of arc_mem_blank_check() (mr.nuke.me@gmail.com)
- arc: regen (te)
- xxx: Regenerate config files (Anton.Kolesov@synopsys.com)
- xxx: Add configure option --disable-libusb0 (Anton.Kolesov@synopsys.com)
- xxx: Add texinfo.tex (Anton.Kolesov@synopsys.com)
- xxx: Add generated configure files (Anton.Kolesov@synopsys.com)
- xxx: Don't use repo.or.cz (Anton.Kolesov@synopsys.com)
- arc: Add Secure MPU registers (Anton.Kolesov@synopsys.com)
- arc: Add descriptions of ARC exception registers (Anton.Kolesov@synopsys.com)
- arc: Support DCCM version 4 (Anton.Kolesov@synopsys.com)
- arc: Clean up types in arc_mem.c (Anton.Kolesov@synopsys.com)
- arc: Fix invalid address range check (Anton.Kolesov@synopsys.com)
- arc: Fix invalid assert in arc_mem_is_slow_memory
  (Anton.Kolesov@synopsys.com)
- arc: Fix unused-but-set-variable warning (Anton.Kolesov@synopsys.com)
- arc: Remove mention of ft2232 interface for windows from documentation
  (Anton.Kolesov@synopsys.com)
- arc: Use FTDI interface on Windows as well for Synopsys boards
  (Anton.Kolesov@synopsys.com)
- arc: Disable wait-until-write-finished for ARC HS in AXS103
  (Anton.Kolesov@synopsys.com)
- arc: Add board file for ARC EM Starter Kit 2.2 (Anton.Kolesov@synopsys.com)
- arc: Rename board files for EM Starter Kit (Anton.Kolesov@synopsys.com)
- arc: Fix a typo in documentation (Anton.Kolesov@synopsys.com)
- arc: Workaround for D$ flushing issue (Anton.Kolesov@synopsys.com)
- arc: Improve warning when breakpoint has been overwritten
  (Anton.Kolesov@synopsys.com)
- arc: Workaround the ARC 600 problem with DEBUG.RA bit
  (Anton.Kolesov@synopsys.com)
- arc: Add DEBUG register to ARCompact (Anton.Kolesov@synopsys.com)
- arc: Prepend '0x' when printing hex number in error message
  (Anton.Kolesov@synopsys.com)
- arc: Decrease JTAG frequency for EM Starter Kit (Anton.Kolesov@synopsys.com)
- arc: Do not wait for JTAG operation success by default
  (Anton.Kolesov@synopsys.com)
- arc: Add documentation for new TCL commands (Anton.Kolesov@synopsys.com)
- arc: Replace literal string with a constant (Anton.Kolesov@synopsys.com)
- arc: Allow register reads from running targets (Anton.Kolesov@synopsys.com)
- arc: Set debug reason properly for actionpoints (Anton.Kolesov@synopsys.com)
- arc: Add definition of DEBUG register type to TCL
  (Anton.Kolesov@synopsys.com)
- arc: Add a commentary about writing registers in examine_target
  (Anton.Kolesov@synopsys.com)
- arc: Add "arc reg" TCL command (Anton.Kolesov@synopsys.com)
- arc: Reset AP_ACx to 0 on target reset (Anton.Kolesov@synopsys.com)
- arc: Set DEBUG.ED for ARC EM (Anton.Kolesov@synopsys.com)
- arc: Do not overwrite DEBUG bits on single step (Anton.Kolesov@synopsys.com)
- arc: Add additional debug output (Anton.Kolesov@synopsys.com)
- arc: Fix a typo comment (Anton.Kolesov@synopsys.com)
- arc: Do not set DEBUG.RA bit in dbg_exit_debug (Anton.Kolesov@synopsys.com)
- arc: Use configurable registers for actionpoints (Anton.Kolesov@synopsys.com)
- arc: Add helper function to set 32-bit registers (Anton.Kolesov@synopsys.com)
- arc: Fix an issue with CCM probing (Anton.Kolesov@synopsys.com)
- arc: Probe for actionpoints availability (Anton.Kolesov@synopsys.com)
- arc: Add command helper for unsigned integer values
  (Anton.Kolesov@synopsys.com)
- arc: Change runcontrol to async mode (Anton.Kolesov@synopsys.com)
- arc: Notify GDB when async run control event occurs
  (Anton.Kolesov@synopsys.com)
- arc: Add support for address actionpoints (Anton.Kolesov@synopsys.com)
- arc: Fix software breakpoints (Anton.Kolesov@synopsys.com)
- arc: Return error if invalid breakpoint size is requested
  (Anton.Kolesov@synopsys.com)
- arc: Do not reset JTAG transaction immediately (Anton.Kolesov@synopsys.com)
- arc: Add reset script for SDP (Anton.Kolesov@synopsys.com)
- Add instructions to build autoconf 2.64 (Anton.Kolesov@synopsys.com)
- arc: Fix mistake with wrong current target in arc_v2_examine_target
  (Anton.Kolesov@synopsys.com)
- arc: Describe ARC-specific commands in documentation
  (Anton.Kolesov@synopsys.com)
- arc: Remove arc32_common->processor_type field (Anton.Kolesov@synopsys.com)
- arc: Introduce target types arc600, arc700 and arcv2
  (Anton.Kolesov@synopsys.com)
- arc: Add AXS103 board support (Anton.Kolesov@synopsys.com)
- Add pkg-config to prerequisites for Windows build
  (Anton.Kolesov@synopsys.com)
- arc: Update instruction for Windows + FTD2XX (Anton.Kolesov@synopsys.com)
- arc: Update copyright headers (Anton.Kolesov@synopsys.com)
- arc: Remove obsolete board and target configurations
  (Anton.Kolesov@synopsys.com)
- arc: Move generic ARC tests to architecture-specific folder
  (Anton.Kolesov@synopsys.com)
- arc: Extract function to add registers (Anton.Kolesov@synopsys.com)
- arc: Extract common code from build_reg_cache functions
  (Anton.Kolesov@synopsys.com)
- arc: Replace temporary code with permanent (Anton.Kolesov@synopsys.com)
- arc: Update CCM recognition code (Anton.Kolesov@synopsys.com)
- arc: Add TCL description for ARC HS targets (Anton.Kolesov@synopsys.com)
- arc: Add TCL description for ARCompact targets (Anton.Kolesov@synopsys.com)
- arc: Set current target in event handlers (Anton.Kolesov@synopsys.com)
- arc: Add support for reduced core register set (Anton.Kolesov@synopsys.com)
- arc: Add TCL description for ARC EM targets (Anton.Kolesov@synopsys.com)
- arc: Fix bogus error message and reduce log level of message
  (Anton.Kolesov@synopsys.com)
- arc: Use better way to read bitfields from structures
  (Anton.Kolesov@synopsys.com)
- arc: Support for 'general' registers (Anton.Kolesov@synopsys.com)
- arc: Support BCR as a special class of registers (Anton.Kolesov@synopsys.com)
- arc: Support multiple register caches (Anton.Kolesov@synopsys.com)
- arc: Add reg-field command (Anton.Kolesov@synopsys.com)
- arc: Implement arc32_get_register_field function (Anton.Kolesov@synopsys.com)
- arc: Implement arc32_get_register_value_u32 function
  (Anton.Kolesov@synopsys.com)
- arc: Add add-reg-type-struct command (Anton.Kolesov@synopsys.com)
- arc: Allow registers to be enabled from TCL (Anton.Kolesov@synopsys.com)
- arc: Add test cases for configurable registers (Anton.Kolesov@synopsys.com)
- arc: Build register cache from TCL-configured registers
  (Anton.Kolesov@synopsys.com)
- arc: Add add-reg function (Anton.Kolesov@synopsys.com)
- arc: Add standard GDB data types (Anton.Kolesov@synopsys.com)
- arc: Add command add-reg-type-flags (Anton.Kolesov@synopsys.com)
- arc: Remove support for GDB compatibility mode (Anton.Kolesov@synopsys.com)
- arc: Update target descriptions to work with GDB 7.9
  (Anton.Kolesov@synopsys.com)
- arc: Fix typo in register name (Anton.Kolesov@synopsys.com)
- arc: Fix invalid file name in documentation (Anton.Kolesov@synopsys.com)
- arc: Update readme (Anton.Kolesov@synopsys.com)
- arc: Fix invalid prerequisite package name in readme
  (Anton.Kolesov@synopsys.com)
- arc: Add a special defconfig for EM SK v1 (Anton.Kolesov@synopsys.com)
- arc: Fix type in register detection code (Anton.Kolesov@synopsys.com)
- arc: Add a NEWS files for ARC-specific changes (Anton.Kolesov@synopsys.com)
- arc: Set proper debug reason when examining the target
  (Anton.Kolesov@synopsys.com)
- arc: Remove debug prints from arc_ocd_examine (Anton.Kolesov@synopsys.com)
- arc: Do not halt targets in board files (Anton.Kolesov@synopsys.com)
- arc: Do not halt target when examining (Anton.Kolesov@synopsys.com)
- arc: Always halt core before doing software reset
  (Anton.Kolesov@synopsys.com)
- arc: Fix TCL CPU definitions (Anton.Kolesov@synopsys.com)
- ft2232: Fix EM Starter Kit v2 support (Anton.Kolesov@synopsys.com)
- arc: Use new reset procedure in our development boards
  (Anton.Kolesov@synopsys.com)
- arc: Add a procedure for software reset (Anton.Kolesov@synopsys.com)
- arc: Support custom reset-assert handlers (Anton.Kolesov@synopsys.com)
- arc: Remove obsolete register commands (Anton.Kolesov@synopsys.com)
- arc: Add aux-reg and core-reg Jim commands (Anton.Kolesov@synopsys.com)
- arc: Remove arc.{c,h} files (Anton.Kolesov@synopsys.com)
- arc: Remove arc_core.{c,h} files (Anton.Kolesov@synopsys.com)
- arc: Remove arc_trgt.{c,h} files (Anton.Kolesov@synopsys.com)
- arc: Remove extra commands (Anton.Kolesov@synopsys.com)
- arc: Add JTAG STATUS.FL checks after each operation
  (Anton.Kolesov@synopsys.com)
- arc: Add a warning when SW breakpoint has been overwritten externally
  (Anton.Kolesov@synopsys.com)
- arc: [trivial] Formatting of AUX register values in log
  (Anton.Kolesov@synopsys.com)
- arc: Add an option to enable paranoia checks for JTAG status RD
  (Anton.Kolesov@synopsys.com)
- arc: Workaround a possible issue with reading DDR memory
  (Anton.Kolesov@synopsys.com)
- arc: Add an artificial delay when reading from DDR memory
  (Anton.Kolesov@synopsys.com)
- arc: Detect CCMs based on BCRs (Anton.Kolesov@synopsys.com)
- arc: Always read BCRs when examining the target (Anton.Kolesov@synopsys.com)
- arc: Add a simple test for STAR 9000830091 (Anton.Kolesov@synopsys.com)
- arc: [trivial] Fix typo with invalid memory address format in log
  (Anton.Kolesov@synopsys.com)
- ARC: Explicitly select JTAG as a transport option
  (Anton.Kolesov@synopsys.com)
- xxx: Rename file with cyryllic symbols (Anton.Kolesov@synopsys.com)
- ARC: Remove unused function arc32_wait_until_core_is_halted
  (Anton.Kolesov@synopsys.com)
- ARC: Update JTAG layer to be compatible with latest OpenOCD
  (Anton.Kolesov@synopsys.com)
- ARC: Do not overwrite DEBUG.UB bit in arc_dbg_enter_debug
  (Anton.Kolesov@synopsys.com)
- ARC: Introduce CHECK_RETVAL macro and use it (Anton.Kolesov@synopsys.com)
- ARC: Fix broken GDB break support (Anton.Kolesov@synopsys.com)
- ARC: Fix invalid JTAG Status masks (Anton.Kolesov@synopsys.com)
- ARC: Add EM StarterKit v2 to configuration scripts
  (Anton.Kolesov@synopsys.com)
- ARC: Fix typo in TCL script for EM SK (Anton.Kolesov@synopsys.com)
- ARC: Fix typo in the filename (Anton.Kolesov@synopsys.com)
- ARC: Improve Windows compatibility (Anton.Kolesov@synopsys.com)
- ARC: Add configuration files for DW ARC AXS102 (Anton.Kolesov@synopsys.com)
- ARC: Update README (Anton.Kolesov@synopsys.com)
- ARC: Add new configurations for EM Starter Kit (Anton.Kolesov@synopsys.com)
- ARC: Add configuration files for DW ARC AXS101 (Anton.Kolesov@synopsys.com)
- ARC: Update docs (Anton.Kolesov@synopsys.com)
- Arc: Fix unaligned 32-bit breakpoints (Anton.Kolesov@synopsys.com)
- Arc: Fix unaligned memory access (Anton.Kolesov@synopsys.com)
- Arc: Fix target definitions for Windows (Anton.Kolesov@synopsys.com)
- Arc: Remove obsolete targets (Anton.Kolesov@synopsys.com)
- Arc: Improve recognition of halt reason examination
  (Anton.Kolesov@synopsys.com)
- Arc: More fixes for 32bit breakpoints (Anton.Kolesov@synopsys.com)
- Arc: Fix error with writing BRK instruction (Anton.Kolesov@synopsys.com)
- Recommend static build of libusb (anton.kolesov@synopsys.com)
- dontmerge: Rename filename with Cyrillic symbols (anton.kolesov@synopsys.com)
- ARC: Add support for GDB XML target description (anton.kolesov@synopsys.com)
- ARC: Remove print core/aux regs commands (anton.kolesov@synopsys.com)
- ARC: Add debug output to read memory function (anton.kolesov@synopsys.com)
- ARC: Remove mentions of maintainer mode in readme
  (anton.kolesov@synopsys.com)
- ARC: Do not print JTAG STATUS register each time (anton.kolesov@synopsys.com)
- ARC: Optimize JTAG layer (anton.kolesov@synopsys.com)
- ARC: Remove JTAG test function (anton.kolesov@synopsys.com)
- ARC: Remove claims that we don't support HS2 (anton.kolesov@synopsys.com)
- ARC: Reorganize log messages (anton.kolesov@synopsys.com)
- ARC: Switch to new ftdi configurations for all targets
  (anton.kolesov@synopsys.com)
- ARC: Remove obsolete Digilent HS configuration (anton.kolesov@synopsys.com)
- ftdi: Add configurations for Digilent HS1 and HS2
  (anton.kolesov@synopsys.com)
- ARC: Conform to C99 integer types format specifiers
  (anton.kolesov@synopsys.com)
- ARC: Fix copyright headers (anton.kolesov@synopsys.com)
- ARC: Fix configuration scripts for Windows (anton.kolesov@synopsys.com)
- ARC: Rewrite README.ARC (anton.kolesov@synopsys.com)
- ARC: Update target description scripts (anton.kolesov@synopsys.com)
- ARC: Remove unused prerequisites from README (anton.kolesov@synopsys.com)
- ARC: Resolve uninitialized pointer (anton.kolesov@synopsys.com)
- ARC: Remove function arc_mem_bulk_write (anton.kolesov@synopsys.com)
- ARC: Reset caches states variables after step (anton.kolesov@synopsys.com)
- Support big endian EM Starter Kit (anton.kolesov@synopsys.com)
- ARC: Add RHEL build instructions (anton.kolesov@synopsys.com)
- ARC: Ensure coherency between caches and memory (anton.kolesov@synopsys.com)
- ARC: Fix support for big endian memory model (anton.kolesov@synopsys.com)
- ARC: Mention EM Starter Kit in readme file (Anton.Kolesov@synopsys.com)
- Document that Digilent HS2 is not supported (akolesov@synopsys.com)
- ARC: Refer to CPU by name instead of id (akolesov@synopsys.com)
- ARC: Add partial support for Digilent HS-2 cable (akolesov@synopsys.com)
- ARC: Optimize bulk operations on AUX registers (akolesov@synopsys.com)
- ARC: Add missing register names for invisible registers
  (akolesov@synopsys.com)
- ARC: Optimize writes and reads of registers (akolesov@synopsys.com)
- ARC: Set target state to HALTED before calling callbacks for event
  (akolesov@synopsys.com)
- ARC: Resolve warnings about keep_alive not called on time
  (akolesov@synopsys.com)
- ARC: Examine whether execution halted due to software breakpoint
  (akolesov@synopsys.com)
- ARC: Update documentation according to user feedback. (akolesov@synopsys.com)
- ARC: Add automake to the list of dependencies (akolesov@synopsys.com)
- arc: Optimize jtag_write_block (mjonker@synopsys.com)
- arc: Write back registers when dirty, not when invalid (mjonker@synopsys.com)
- arc: Get rid of even more debug prints (mjonker@synopsys.com)
- arc: Get rid of a lot of debug prints (mjonker@synopsys.com)
- arc: Reduce sleep times in arc_dbg from 1 s to 1 ms (mjonker@synopsys.com)
- arc: Handle multiple size!=4 writes in arc_mem_write_block
  (mjonker@synopsys.com)
- arc: Get rid of some debug prints in arc_mem (mjonker@synopsys.com)
- arc: Use read_aux_reg for auxiliary registers (mjonker@synopsys.com)
- arc: Invalidate D$ as well (mjonker@synopsys.com)
- Fix wait_until_core_is_halted() (mischa@mischa-VirtualBox.(none))
- arc: Fix memory read/write routines to handle unaligned addresses
  (mischa@mischa-VirtualBox.(none))
- ARC: ARC source code guide included in doc/README.ARC
  (frank.dols@synopsys.com)
- ARC: bootstrap script isn't necessary anymore to call for build on Linux
  (frank.dols@synopsys.com)
- ARC: solve link error on missing .soft_reset_halt_imp
  (frank.dols@synopsys.com)
- ARC: register list print style update (frank.dols@synopsys.com)
- ARC: put Synosys getting started manual in OSS README.xxx style
  (frank.dols@synopsys.com)
- Merge branch 'claudiu-win_crosscompilation-mods' of git@github.com:foss-for-
  synopsys-dwc-arc-processors/openocd.git into arc-0.7.0-dev-00151
  (frank.dols@synopsys.com)
- ARC: prevent from missing version.texi file when generating documentation
  (frank.dols@synopsys.com)
- ARC: build instruction how to build for Windows host
  (frank.dols@synopsys.com)
- ARC: set proper CPUid for ARC700 on ML509 (frank.dols@synopsys.com)
- ARC: insert instruction cache flash on set_breakpoint
  (frank.dols@synopsys.com)
- ARC: prevent from reading/writing none existing core registers
  particularly ARC-EM4 core registers r61 or r62 (frank.dols@synopsys.com)
- ARC: how to program FPGA with Digilent HS1 probe  >$ djtgcfg -d JtagHs2 prog
  -i 4 -f <fpga bit file to progam>.bit (frank.dols@synopsys.com)
- ARC: add arc600 support (frank.dols@synopsys.com)
- ARC: monitor arc set-core-into-halted + print-core-status
  (frank.dols@synopsys.com)
- ARC: target configuration files incl. arc600 (frank.dols@synopsys.com)
- ARC: reorganized content of getting started manual (frank.dols@synopsys.com)
- ARC: give us processor type switch support (frank.dols@synopsys.com)
- ARC: throw ARC700 out (frank.dols@synopsys.com)
- ARC: user manual update on telnet connectivity (frank.dols@synopsys.com)
- ARC: move debug functions to the debug module (frank.dols@synopsys.com)
- ARC: info how to compile/run for developer versus customer
  (frank.dols@synopsys.com)
- ARC: code cleanup on printf -> LOG_DEBUG/INFO/WARNING/USER
  (frank.dols@synopsys.com)
- ARC: increase fastmem block size (frank.dols@synopsys.com)
- ARC: (gdb)monitor arc read/write-mem-word (frank.dols@synopsys.com)
- ARC: gettingstarted.txt on compiling and starting (frank.dols@synopsys.com)
- ARC: openocd.cfg for bottlenose and ml509 (frank.dols@synopsys.com)
- ARC: remove not supported targets (frank.dols@synopsys.com)
- ARC: minor text update (frank.dols@synopsys.com)
- ARC: mv openocd.cfg into tcl/target/snps_haps51_arc700.cfg
  (frank.dols@synopsys.com)
- ARC: add monitor cmds to read/write core & aux regs (frank.dols@synopsys.com)
- ARC: intro to all new modules (frank.dols@synopsys.com)
- ARC: generic (arc32) functions stack module interface
  (frank.dols@synopsys.com)
- ARC: arc700 OpenOCD interface (frank.dols@synopsys.com)
- ARC: debug functions stack module interface (frank.dols@synopsys.com)
- ARC: core functions stack module interface (frank.dols@synopsys.com)
- ARC: memory functions stack module interface (frank.dols@synopsys.com)
- ARC: OpenOCD functions stack module interface (frank.dols@synopsys.com)
- ARC: target functions stack module interface (frank.dols@synopsys.com)
- ARC: give us code single stepping (frank.dols@synopsys.com)
- ARC: debug_log cleanup on regs (frank.dols@synopsys.com)
- ARC: do not give tons of debug log with -d3 on JTAG (frank.dols@synopsys.com)
- ARC: wait_until_core_is_halted func (frank.dols@synopsys.com)
- ARC: arc32: give us specific core state manipulation   Further more, strip
  out module specifics   and migrate to single arc.h include.
  (frank.dols@synopsys.com)
- ARC: arc700: give "break" "continue" "step" features   Further more, strip
  out module specifics   and migrate to single arc.h include.
  (frank.dols@synopsys.com)
- ARC: migrate to the one "arc.h" include (frank.dols@synopsys.com)
- ARC: arc_mntr (monitor commands) module (frank.dols@synopsys.com)
- ARC: arc_regs (register access) module (frank.dols@synopsys.com)
- ARC: Makefile update for new modules mntr & regs (frank.dols@synopsys.com)
- ARC: Getting started update on GDB monitor (frank.dols@synopsys.com)
- ARC: add step to debug stepping and resuming (frank.dols@synopsys.com)
- ARC: tweaked arc-jtag io calls (frank.dols@synopsys.com)
- ARC: provide generic debug functions (frank.dols@synopsys.com)
- ARC: fix typedef scoping of target_type (frank.dols@synopsys.com)
- ARC: prevent us from "Error: GDB missing ack(2) - assumed good"
  (frank.dols@synopsys.com)
- ARC: get us into add breakpoint and first step (frank.dols@synopsys.com)
- ARC: reorganize register map ifo arc-elf32-gdb v7.5.1
  (frank.dols@synopsys.com)
- ARC: write block to memory & transaction reset (frank.dols@synopsys.com)
- ARC: doc update on startup sequence + gdb connection
  (frank.dols@synopsys.com)
- ARC: introduce write file to memory (frank.dols@synopsys.com)
- ARC: provide generic register and memory access functions
  (frank.dols@synopsys.com)
- ARC: add read and write to/from memory (frank.dols@synopsys.com)
- ARC: give us space to store image to load (frank.dols@synopsys.com)
- ARC: introduce ARC to the build system (frank.dols@synopsys.com)
- ARC: initial config scripts to tcl/board|cpu/arc|target
  (frank.dols@synopsys.com)
- ARC: introduce the arc700 to src/target (frank.dols@synopsys.com)
- ARC: introduce the arc_jtag to src/target (frank.dols@synopsys.com)
- ARC: introduce the arc32 to src/target (frank.dols@synopsys.com)
- ARC Give us a plain text Getting started manual. (frank.dols@synopsys.com)
- Initial commit (frank.dols@synopsys.com)

* Mon Jul 24 2017 Alexandru Gagniuc <mr.nuke.me@gmail.com> - 0.10.0-3
- Rebase on Synopsis 0.10 branch
- Add Adaptrum Endor Quad SPI flash controller driver

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
