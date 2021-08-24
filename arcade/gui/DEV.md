## GUI v2

## Docs

### Widgets

UI components are represented as Widgets

Widget:

- Has a rectangle
- Provide render function to be drawn

Wrapper:

- Widgets containing exactly one child widget
- Apply padding around the child widget

Group:

- Widgets containing multiple child widgets

Available Widgets:

- Widgets:
    - FlatButton
    - InputText
    - TextArea
- Wrapper:
    - Padding
    - Border
    - AnchorWidget
- Groups
    - BoxGroup

### UIEvents
UIEvents are fully typed dataclasses, which provide information about a event effecting the UI. Events are passed top down by the UIManager.

General pyglet window events are converted by the UIManager into UIEvents and passed via dispatch_event to the on_event callbacks.

Widget specific UIEvents like UIOnClick are dispatched via "on_event" and are then  dispatched as specific event types (like 'on_click')

UIEventTypes:
- UIEvent
- UIMouseEvent
- UIMouseMovement
- UIMousePress
- UIMouseDrag
- UIMouseRelease
- UIMouseScroll
- UITextEvent
- UITextMotion
- UITextMotionSelect
- UIOnClick

## Decisions

- Widgets.do_layout is allowed to change their own rectangle and align children's rectangle
- Widgets can ask children to resize to a given rect (TODO)
- Widget's rect should not be resized from outside directly

## Chors
- [ ] Can UIManager be a Widget on its own?
- [ ] BoxGroup might show strange behavior through different call orders (do_layout,add,remove)