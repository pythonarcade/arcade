<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.2" tiledversion="1.2.4" name="items" tilewidth="128" tileheight="128" tilecount="24" columns="0">
 <grid orientation="orthogonal" width="1" height="1"/>
 <tile id="0">
  <properties>
   <property name="Points" value="1"/>
  </properties>
  <image width="128" height="128" source="../images/items/coinBronze.png"/>
  <objectgroup draworder="index">
   <object id="2" x="32" y="32" width="64" height="64">
    <ellipse/>
   </object>
  </objectgroup>
 </tile>
 <tile id="1">
  <properties>
   <property name="Points" value="10"/>
  </properties>
  <image width="128" height="128" source="../images/items/coinGold.png"/>
  <objectgroup draworder="index">
   <object id="1" x="32" y="32" width="64" height="64">
    <ellipse/>
   </object>
  </objectgroup>
 </tile>
 <tile id="2">
  <properties>
   <property name="Points" value="5"/>
  </properties>
  <image width="128" height="128" source="../images/items/coinSilver.png"/>
  <objectgroup draworder="index">
   <object id="1" x="32" y="32" width="64" height="64">
    <ellipse/>
   </object>
  </objectgroup>
 </tile>
 <tile id="3">
  <image width="128" height="128" source="../images/items/flagGreen_down.png"/>
  <objectgroup draworder="index">
   <object id="1" x="0" y="0" width="32" height="128"/>
  </objectgroup>
 </tile>
 <tile id="4">
  <properties>
   <property name="Points" value="25"/>
  </properties>
  <image width="128" height="128" source="../images/items/flagGreen1.png"/>
  <animation>
   <frame tileid="4" duration="500"/>
   <frame tileid="5" duration="500"/>
  </animation>
 </tile>
 <tile id="5">
  <image width="128" height="128" source="../images/items/flagGreen2.png"/>
 </tile>
 <tile id="6">
  <image width="128" height="128" source="../images/items/flagRed_down.png"/>
 </tile>
 <tile id="7">
  <image width="128" height="128" source="../images/items/flagRed1.png"/>
 </tile>
 <tile id="8">
  <image width="128" height="128" source="../images/items/flagRed2.png"/>
 </tile>
 <tile id="9">
  <image width="128" height="128" source="../images/items/flagYellow_down.png"/>
 </tile>
 <tile id="10">
  <image width="128" height="128" source="../images/items/flagYellow1.png"/>
 </tile>
 <tile id="11">
  <image width="128" height="128" source="../images/items/flagYellow2.png"/>
 </tile>
 <tile id="12">
  <image width="128" height="128" source="../images/items/gemBlue.png"/>
  <objectgroup draworder="index">
   <object id="1" x="42.5455" y="41.0909">
    <polygon points="0,0 -13.8182,19.2727 -13.4545,24.1818 21.6364,47.0909 55.8182,24.9091 56,18.5455 42.5455,-0.545455"/>
   </object>
  </objectgroup>
 </tile>
 <tile id="13">
  <image width="128" height="128" source="../images/items/gemGreen.png"/>
 </tile>
 <tile id="14">
  <image width="128" height="128" source="../images/items/gemRed.png"/>
 </tile>
 <tile id="15">
  <image width="128" height="128" source="../images/items/gemYellow.png"/>
 </tile>
 <tile id="16">
  <image width="128" height="128" source="../images/items/keyBlue.png"/>
 </tile>
 <tile id="17">
  <image width="128" height="128" source="../images/items/keyGreen.png"/>
 </tile>
 <tile id="18">
  <image width="128" height="128" source="../images/items/keyRed.png"/>
 </tile>
 <tile id="19">
  <image width="128" height="128" source="../images/items/keyYellow.png"/>
 </tile>
 <tile id="20">
  <image width="128" height="128" source="../images/items/star.png"/>
 </tile>
 <tile id="21">
  <image width="128" height="128" source="../images/tiles/torch1.png"/>
 </tile>
 <tile id="22">
  <image width="128" height="128" source="../images/tiles/torch2.png"/>
  <animation>
   <frame tileid="21" duration="400"/>
   <frame tileid="22" duration="400"/>
  </animation>
 </tile>
 <tile id="23">
  <image width="128" height="128" source="../images/tiles/torchOff.png"/>
 </tile>
</tileset>
