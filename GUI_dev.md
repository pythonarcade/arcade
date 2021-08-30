# Arcade GUI 2.0 (alpha)


Doc structure

* Overview: basic goal and important classes
* Layout: Concept and Usage
* Events: Which events do exist
* API:
  * UIManager / UILayoutManager
  * UILayouts
  * UIElements
    * ...
  * Other
    * UIEvent
    * util methods
* Planned ?





## Changelog

* New UIManager -> UILayoutManager
  * provides entry for layouting
  * does not register `on_draw` callback
    
* UIElements
  * min_size
  * size_hint
  
* Changed Constructor


* Available Layouts
  * UILayout
    * Abstract layout class
  * UIBoxLayout
    * vertical and horizontal orientation
    * background and border may be set
    * background can be `arcade.Color` or an image path
    * support for padding (space between border and elements)
    * margin between elements can be achieved with `space`
  * Anchor Layout
    * used as root layout in UILayoutManager
    * position children relative to top, right, bottom, left, center_x, center_y
    * children UILayouts can be expanded using `fill_x` or 'fill_y'
    * 🐛 missing support for padding, border, bg

### Planned features

* [x] Remove elements from UIManager
* [x] UIElements size can be influenced by UILayout
* [x] Layer support on UIManager
* [ ] Hide UI and disable input
* [ ] Grid Layout
* [ ] Spacing in BoxLayout




## Concepts:

### 

#### The layout algorithm is influenced by:
* Unity3d Auto Layout
    * Widgets provide minimum, preferred and flexible width
    * [Doc](https://docs.unity3d.com/Packages/com.unity.ugui@1.0/manual/UIAutoLayout.html)

* tkinter
    * add widget with ´pack(child)´
* Kivy:
    * Layout uses size_hint and pos_hint of child
      * size_hint: 0-1, fraction of the parents size
      * pos_hint: place relative to parent
      * if the values are set to None, layout will not change the acording property
    * Layout.do_layout(*largs) used to trigger layouting
    * Layout.minimum_height/width/size automatic computet value to contain all children
    * Layout.padding: Padding
    * Layout.spacing: space between elements
* Qt