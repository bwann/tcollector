# A really quick Chef recipe snippet to show where to install the SMF
# manifest and how to import it with svccfg if needed on Solaris-ish
# systems if it's not already there.

case node['platform_family']
when 'openindiana'

  # We're so fancy we have a real SMF manifest!
  cookbook_file '/var/svc/manifest/application/tcollector.xml' do
    source 'tcollector.xml'
    mode '0750'
  end

  execute 'import_manifest' do
    command 'svccfg -v import /var/svc/manifest/application/tcollector.xml'
    not_if 'svcs -H svc:/application/tcollector'
  end

end
