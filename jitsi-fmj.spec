%{?_javapackages_macros:%_javapackages_macros}

# NOTE:	fmj is quite an old piece of software and not more so used at
#	these days. Because is it a bit complex to build all and actually
#	only libjitsi requires it, only classes really used by libjitsi
#	are compiled (i.e. ant build is skipped).

%define debug_package %{nil}

Summary:	Free replacement for the JMF (Java Media Framework)
Name:		fmj
Version:	20170201
Release:	0
License:	LGPLv3
Group:		Development/Java
URL:		http://fmj-sf.net/
# cvs repo:
# cvs -d:pserver:anonymous@fmj.cvs.sourceforge.net:/cvsroot/fmj login
# cvs -z3 -d:pserver:anonymous@fmj.cvs.sourceforge.net:/cvsroot/fmj co -P fmj
# cp -far fmj fmj-20170201
# find fmj-20170201 -name CVS -type d -exec rm -fr {} \; 2> /dev/null
# tar Jcf fmj-20170201.tar.xz fmj-20170201
# svn repo:
# svn checkout svn://svn.code.sf.net/p/fmj/code/fmj fmj-code
# cp -far fmj-code fmj-20170201
# find fmj-20170201 -name \.svn -type d -exec rm -fr ./{} \; 2> /dev/null
# tar cJf fmj-20170201.tar.xz fmj-20170201/
Source0:	fmj-%{version}.tar.xz

BuildRequires:	maven-local
BuildRequires:	mvn(junit:junit)
BuildRequires:	mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:	mvn(org.apache.maven.plugins:maven-source-plugin)
BuildRequires:	mvn(org.codehaus.mojo:build-helper-maven-plugin)

%description
FMJ is an open-source project with the goal of providing a
replacement or alternative to Java Media Framework (JMF).

It aims to produce a single API/Framework which can be used to
capture, playback, process and stream media across multiple
platforms.

%files -f .mfiles
%dir %{_javadir}/%{name}/
%{_javadir}/%{name}/*.properties
%doc README
%doc todo.txt
%doc version-history.txt
%doc LICENSE

#----------------------------------------------------------------------------

%package javadoc
Summary:	Javadoc for %{name}
BuildArch:	noarch

%description javadoc
API documentation for %{name}.

%files javadoc -f .mfiles-javadoc
%doc LICENSE

#----------------------------------------------------------------------------

%prep
%setup -q -n fmj-%{version}
# Delete all prebuild JARs and libs
find . -name "*.jar" -delete
find . -name "*.class" -delete
find . -name "*.so" -delete

# remove windows and mac stuff
rm -r nativelib/win32-x86
rm -r sh/win32
rm -r sh/macosx

# adjust path for the samples
sed -i -e 's|samplemedia|%{_datadir}/%{name}|g' \
	src.fmjstudio/net/sf/fmj/ui/application/PlayerPanel.java

# adjust path for logging.properties
sed -i -e 's|logging.properties|%{_javadir}/%{name}/logging.properties|g' \
	src/net/sf/fmj/utility/FmjStartup.java

# Remove parent
%pom_remove_parent ./m2/jitsi/pom.xml

# Add groupId
%pom_xpath_inject "pom:project" "
	<groupId>org.jitsi</groupId>" ./m2/jitsi/pom.xml

# Update version
%pom_xpath_replace "pom:project/pom:version" "
	<version>1.0.0</version>" ./m2/jitsi/pom.xml

# Fix missing version warnings
%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-compiler-plugin']]" "
	<version>any</version>" ./m2/jitsi/pom.xml
%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='build-helper-maven-plugin']]" "
	<version>any</version>" ./m2/jitsi/pom.xml
%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-bundle-plugin']]" "
	<version>any</version>" ./m2/jitsi/pom.xml
%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-source-plugin']]" "
	<version>any</version>" ./m2/jitsi/pom.xml

# Add an OSGi compilant MANIFEST.MF
%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-bundle-plugin']]" \
	"<extensions>true</extensions>" ./m2/jitsi/pom.xml

# Add the META-INF/INDEX.LIST (fix jar-not-indexed warning) and
# the META-INF/MANIFEST.MF to the jar archive
%pom_add_plugin :maven-jar-plugin ./m2/jitsi/pom.xml "
<executions>
	<execution>
		<phase>package</phase>
		<configuration>
			<archive>
				<manifestFile>\${project.build.outputDirectory}/META-INF/MANIFEST.MF</manifestFile>
				<manifest>
					<addDefaultImplementationEntries>true</addDefaultImplementationEntries>
					<addDefaultSpecificationEntries>true</addDefaultSpecificationEntries>
				</manifest>
				<index>true</index>
			</archive>
		</configuration>
		<goals>
			<goal>jar</goal>
		</goals>
	</execution>
</executions>"

%build
%mvn_build -- -f ./m2/jitsi/pom.xml -Dproject.build.sourceEncoding=UTF-8

%install
%mvn_install

# logging.properties
install -dm 0755 %{buildroot}%{_javadir}/%{name}/
install -pm 0644 *.properties %{buildroot}%{_javadir}/%{name}/

