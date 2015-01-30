#------------------- package info ----------------------------------------------

#
# enter the simple app name, e.g. myapp
#
Name: %{getenv:NAME}

#
# enter the app version, e.g. 0.0.1
#
Version: %{getenv:VERSION}

#
# enter the release; start with fasrc01 (or some other convention for your 
# organization) and increment in subsequent releases
#
# the actual "Release", %%{release_full}, is constructed dynamically; for Comp 
# and MPI apps, it will include the name/version/release of the apps used to 
# build it and will therefore be very long
#
%define release_short %{getenv:RELEASE}

#
# enter your FIRST LAST <EMAIL>
#
Packager: %{getenv:FASRCSW_AUTHOR}

#
# enter a succinct one-line summary (%%{summary} gets changed when the debuginfo 
# rpm gets created, so this stores it separately for later re-use); do not 
# surround this string with quotes
#
%define summary_static an open-source, multi-platform data analysis and visualization application
Summary: %{summary_static}

#
# enter the url from where you got the source; change the archive suffix if 
# applicable
#
URL: http://www.paraview.org/
#wget 'http://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v4.1&type=binary&os=linux64&downloadFile=ParaView-4.1.0-Linux-64bit-glibc-2.3.6.tar.gz' -O ParaView-4.1.0-Linux-64bit-glibc-2.3.6.tar.gz
Source: ParaView-%{version}-Linux-64bit-glibc-2.3.6.tar.gz

#
# there should be no need to change the following
#

#these fields are required by RPM
Group: fasrcsw
License: see COPYING file or upstream packaging

#this comes here since it uses Name and Version but dynamically computes Release, Prefix, etc.
%include fasrcsw_defines.rpmmacros

Release: %{release_full}
Prefix: %{_prefix}


#
# enter a description, often a paragraph; unless you prefix lines with spaces, 
# rpm will format it, so no need to worry about the wrapping
#
%description
ParaView is an open-source, multi-platform data analysis and visualization application. ParaView users can quickly build visualizations to analyze their data using qualitative and quantitative techniques. The data exploration can be done interactively in 3D or programmatically using ParaView’s batch processing capabilities.



#------------------- %%prep (~ tar xvf) ---------------------------------------

%prep


#
# unpack the sources here.  The default below is for standard, GNU-toolchain 
# style things -- hopefully it'll just work as-is.
#

umask 022
cd "$FASRCSW_DEV"/rpmbuild/BUILD 
rm -rf %{name}-%{version}
tar xvf "$FASRCSW_DEV"/rpmbuild/SOURCES/ParaView-%{version}-Linux-64bit-glibc-2.3.6.tar.*
mv ParaView-%{version}-Linux-64bit %{name}-%{version}
cd %{name}-%{version}
chmod -Rf a+rX,u+w,g-w,o-w .



#------------------- %%build (~ configure && make) ----------------------------

%build

#(leave this here)
%include fasrcsw_module_loads.rpmmacros


#
# configure and make the software here.  The default below is for standard 
# GNU-toolchain style things -- hopefully it'll just work as-is.
# 

##prerequisite apps (uncomment and tweak if necessary).  If you add any here, 
##make sure to add them to modulefile.lua below, too!
#module load NAME/VERSION-RELEASE



#------------------- %%install (~ make install + create modulefile) -----------

%install

#(leave this here)
%include fasrcsw_module_loads.rpmmacros


#
# make install here.  The default below is for standard GNU-toolchain style 
# things -- hopefully it'll just work as-is.
#
# Note that DESTDIR != %{prefix} -- this is not the final installation.  
# Rpmbuild does a temporary installation in the %{buildroot} and then 
# constructs an rpm out of those files.  See the following hack if your app 
# does not support this:
#
# https://github.com/fasrc/fasrcsw/blob/master/doc/FAQ.md#how-do-i-handle-apps-that-insist-on-writing-directly-to-the-production-location
#
# %%{buildroot} is usually ~/rpmbuild/BUILDROOT/%{name}-%{version}-%{release}.%{arch}.
# (A spec file cannot change it, thus it is not inside $FASRCSW_DEV.)
#

umask 022
cd "$FASRCSW_DEV"/rpmbuild/BUILD/%{name}-%{version}
echo %{buildroot} | grep -q %{name}-%{version} && rm -rf %{buildroot}
mkdir -p %{buildroot}/%{_prefix}

rsync -av ./ %{buildroot}/%{_prefix}/


#(this should not need to be changed)
#these files are nice to have; %%doc is not as prefix-friendly as I would like
#if there are other files not installed by make install, add them here
for f in COPYING AUTHORS README INSTALL ChangeLog NEWS THANKS TODO BUGS; do
	test -e "$f" && ! test -e '%{buildroot}/%{_prefix}/'"$f" && cp -a "$f" '%{buildroot}/%{_prefix}/'
done

#(this should not need to be changed)
#this is the part that allows for inspecting the build output without fully creating the rpm
%if %{defined trial}
	set +x
	
	echo
	echo
	echo "*************** fasrcsw -- STOPPING due to %%define trial yes ******************"
	echo 
	echo "Look at the tree output below to decide how to finish off the spec file.  (\`Bad"
	echo "exit status' is expected in this case, it's just a way to stop NOW.)"
	echo
	echo
	
	tree '%{buildroot}/%{_prefix}'

	echo
	echo
	echo "Some suggestions of what to use in the modulefile:"
	echo
	echo

	generate_setup.sh --action echo --format lmod --prefix '%%{_prefix}'  '%{buildroot}/%{_prefix}'

	echo
	echo
	echo "******************************************************************************"
	echo
	echo
	
	#make the build stop
	false

	set -x
%endif

# 
# FIXME (but the above is enough for a "trial" build)
#
# This is the part that builds the modulefile.  However, stop now and run 
# `make trial'.  The output from that will suggest what to add below.
#
# - uncomment any applicable prepend_path things (`--' is a comment in lua)
#
# - do any other customizing of the module, e.g. load dependencies -- make sure 
#   any dependency loading is in sync with the %%build section above!
#
# - in the help message, link to website docs rather than write anything 
#   lengthy here
#
# references on writing modules:
#   http://www.tacc.utexas.edu/tacc-projects/lmod/advanced-user-guide/writing-module-files
#   http://www.tacc.utexas.edu/tacc-projects/lmod/system-administrator-guide/initial-setup-of-modules
#   http://www.tacc.utexas.edu/tacc-projects/lmod/system-administrator-guide/module-commands-tutorial
#

mkdir -p %{buildroot}/%{_prefix}
cat > %{buildroot}/%{_prefix}/modulefile.lua <<EOF
local helpstr = [[
%{name}-%{version}-%{release_short}
%{summary_static}
]]
help(helpstr,"\n")

whatis("Name: %{name}")
whatis("Version: %{version}-%{release_short}")
whatis("Description: %{summary_static}")

---- prerequisite apps (uncomment and tweak if necessary)
--if mode()=="load" then
--	if not isloaded("NAME") then
--		load("NAME/VERSION-RELEASE")
--	end
--end

-- environment changes (uncomment what's relevant)
prepend_path("PATH",               "%{_prefix}/bin")
prepend_path("CPATH",              "%{_prefix}/lib/paraview-4.1/lib/python2.7/site-packages/numpy/distutils/tests/f2py_f90_ext/include")
prepend_path("CPATH",              "%{_prefix}/lib/paraview-4.1/lib/python2.7/site-packages/numpy/core/include")
prepend_path("CPATH",              "%{_prefix}/lib/paraview-4.1/lib/python2.7/site-packages/numpy/numarray/include")
prepend_path("CPATH",              "%{_prefix}/lib/paraview-4.1/include")
prepend_path("CPATH",              "%{_prefix}/lib/paraview-4.1/site-packages/mpi4py/include")
prepend_path("FPATH",              "%{_prefix}/lib/paraview-4.1/lib/python2.7/site-packages/numpy/distutils/tests/f2py_f90_ext/include")
prepend_path("FPATH",              "%{_prefix}/lib/paraview-4.1/lib/python2.7/site-packages/numpy/core/include")
prepend_path("FPATH",              "%{_prefix}/lib/paraview-4.1/lib/python2.7/site-packages/numpy/numarray/include")
prepend_path("FPATH",              "%{_prefix}/lib/paraview-4.1/include")
prepend_path("FPATH",              "%{_prefix}/lib/paraview-4.1/site-packages/mpi4py/include")
prepend_path("LD_LIBRARY_PATH",    "%{_prefix}/lib")
prepend_path("LD_LIBRARY_PATH",    "%{_prefix}/lib/paraview-4.1/lib")
prepend_path("LD_LIBRARY_PATH",    "%{_prefix}/lib/paraview-4.1/lib/python2.7/site-packages/numpy/lib")
prepend_path("LD_LIBRARY_PATH",    "%{_prefix}/lib/paraview-4.1/lib/python2.7/site-packages/numpy/core/lib")
prepend_path("LD_LIBRARY_PATH",    "%{_prefix}/share/paraview-4.1/www/lib")
prepend_path("LIBRARY_PATH",       "%{_prefix}/lib")
prepend_path("LIBRARY_PATH",       "%{_prefix}/lib/paraview-4.1/lib")
prepend_path("LIBRARY_PATH",       "%{_prefix}/lib/paraview-4.1/lib/python2.7/site-packages/numpy/lib")
prepend_path("LIBRARY_PATH",       "%{_prefix}/lib/paraview-4.1/lib/python2.7/site-packages/numpy/core/lib")
prepend_path("LIBRARY_PATH",       "%{_prefix}/share/paraview-4.1/www/lib")
prepend_path("PYTHONPATH",         "%{_prefix}/lib/paraview-4.1/lib/python2.7/site-packages")
prepend_path("PYTHONPATH",         "%{_prefix}/lib/paraview-4.1/site-packages")
EOF



#------------------- %%files (there should be no need to change this ) --------

%files

%defattr(-,root,root,-)

%{_prefix}/*



#------------------- scripts (there should be no need to change these) --------


%pre
#
# everything in fasrcsw is installed in an app hierarchy in which some 
# components may need creating, but no single rpm should own them, since parts 
# are shared; only do this if it looks like an app-specific prefix is indeed 
# being used (that's the fasrcsw default)
#
echo '%{_prefix}' | grep -q '%{name}.%{version}' && mkdir -p '%{_prefix}'
#

%post
#
# symlink to the modulefile installed along with the app; we want all rpms to 
# be relocatable, hence why this is not a proper %%file; as with the app itself, 
# modulefiles are in an app hierarchy in which some components may need 
# creating
#
mkdir -p %{modulefile_dir}
ln -s %{_prefix}/modulefile.lua %{modulefile}
#


%preun
#
# undo the module file symlink done in the %%post; do not rmdir 
# %%{modulefile_dir}, though, since that is shared by multiple apps (yes, 
# orphans will be left over after the last package in the app family 
# is removed)
#
test -L '%{modulefile}' && rm '%{modulefile}'
#

%postun
#
# undo the last component of the mkdir done in the %%pre (yes, orphans will be 
# left over after the last package in the app family is removed); also put a 
# little protection so this does not cause problems if a non-default prefix 
# (e.g. one shared with other packages) is used
#
test -d '%{_prefix}' && echo '%{_prefix}' | grep -q '%{name}.%{version}' && rmdir '%{_prefix}'
#


%clean
#
# wipe out the buildroot, but put some protection to make sure it isn't 
# accidentally / or something -- we always have "rpmbuild" in the name
#
echo '%{buildroot}' | grep -q 'rpmbuild' && rm -rf '%{buildroot}'
#