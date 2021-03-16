# Arcade GUI 2.0 (alpha)


## Changelog

* New UIManager -> UILayoutManager
  * provides entry for layouting
  * does not register `on_draw` callback
    

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

### Layouts

UILayout manages UIElements or Sprites.
´UILayout.pack´ adds a child to this layout.
Layout specific ´**kwargs´ may be used.

UILayouts do change positions of children.

Sprites, UIElements, and UILayouts have width and height.
These values represent the current size of the element.

Sprites, UIElements and UILayouts may provide `min_size` and `size_hint`.

> `min_size` defines the minimal size the element has to get in pixel.
>
> `size_hint` defines how much of the parents space it would like to occupy (range: 0.0-1.0).
>  
> For maximal vertical and horizontal expansion, define `size_hint` of 1 for the axis.
 
UILayouts are allowed to change the width and height of children
which define at least one of these properties.
While most of UIElements provide a default behavior to be used in UILayouts, Sprites do not.
Sprites, UIElements, and UILayouts which allow size manipulation have to adust to the set width and height. For this they should provide `resize(width, height)`.

> The resize callback is used to prevent duplicate adjustments for setting width and height.


### Layouting

`UILayout.do_layout()` starts the layouting process. While `do_layout` does provide a default implementation, every subclass of UILayout have to implement `UILayout.place_elements()`.


Executed steps within do_layout:
1. call `self.place_elements()`
    1. collect min_size, size_hint and size of all children
    2. calculate the new position and sizes
    3. set position and size of children
2. recursive call `do_layout` on child layouts


```puml
@startuml

!include https://raw.githubusercontent.com/bschwarz/puml-themes/master/themes/cerulean-outline/puml-theme-cerulean-outline.puml

UIManager -> UILayout ++ : do_layout()
    group place_elements()
        UILayout <- children: get min_size, size_hint, size
        UILayout -> children: set size and pos
    end
    
    loop sub layouts
        UILayout -> children: do_layout()
    end

    return
@enduml
```

### Behavior of Components

`*` implementation details, that might change later

#### UIAnchorLayout

- expands to full parents space
- children may overlap*

Pack kwargs:
- top
- bottom
- left
- right
- center_x
- center_y
- space

> top, bottom, ... do use the according elements edge to aline. That means `bottom=30` will place the element with 30 pixel distance between viewports bottom and elements bottom edge. 

#### UIBoxLayout

- wraps content
- children will not overlap
- overflow not handled*

Pack kwargs:
- 

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