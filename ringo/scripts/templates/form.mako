<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<configuration>
  <source>
    <!-- Define different entity types -->
    <!-- This field is only a Dummy field as example which is not really in the database -->
    <entity id="e1" name="dummy" label="Dummy" type="string"/>
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
