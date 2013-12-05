<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<configuration xmlns:i18n="http://xml.zope.org/namespaces/i18n" i18n:domain="ringo">
  <source>
    <!-- Define different entity types -->
    <!-- This field is only a Dummy field as example which is not really in the database -->
    <entity i18n:attributes="label" id="e1" name="dummy" label="Dummy" type="string"/>
  </source>
  <form id="create" autocomplete="off" method="POST" action="" enctype="multipart/form-data">
    <snippet ref="create_snippet"/>
  </form>
  <form id="update" autocomplete="off" method="POST" action="" enctype="multipart/form-data">
    <snippet ref="create_snippet"/>
  </form>
  <form id="read" readonly="true">
    <snippet ref="create_snippet"/>
  </form>

  <!-- Create-->
  <snippet id="create_snippet">
    <snippet ref="s1"/>
  </snippet>

  <!-- Role -->
  <snippet id="s1">
    <row>
      <col><field ref="e1"/></col>
    </row>
  </snippet>
</configuration>
