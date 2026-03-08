from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

from arcade.gl import enums
from arcade.gl.query import Query

if TYPE_CHECKING:
    from pyglet.graphics.api.webgl.webgl_js import WebGLQuery as JSWebGLQuery

    from arcade.gl.backends.webgl.context import WebGLContext


class WebGLQuery(Query):
    __slots__ = (
        "_glo_samples_passed",
        "_glo_time_elapsed",
        "_glo_primitives_generated",
    )

    def __init__(self, ctx: WebGLContext, samples=True, time=False, primitives=True):
        super().__init__(ctx, samples, time, primitives)
        self._ctx = ctx

        if time:
            raise NotImplementedError("Time queries are not supported with WebGL")

        glos = []

        self._glo_samples_passed = None
        if self._samples_enabled:
            self._glo_samples_passed = self._ctx._gl.createQuery()
            glos.append(self._glo_samples_passed)

        self._glo_primitives_generated = None
        if self._primitives_enabled:
            self._glo_primitives_generated = self._ctx._gl.createQuery()
            glos.append(self._glo_primitives_generated)

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, WebGLQuery.delete_glo, self._ctx, glos)

    def __enter__(self):
        if self._samples_enabled:
            self._ctx._gl.beginQuery(enums.ANY_SAMPLES_PASSED, self._glo_samples_passed)  # type: ignore
        if self._primitives_enabled:
            self._ctx._gl.beginQuery(
                enums.TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN,
                self._glo_primitives_generated,  # type: ignore
            )

    def __exit__(self):
        if self._samples_enabled:
            self._ctx._gl.endQuery(enums.ANY_SAMPLES_PASSED)
            self._samples = self._ctx._gl.getQueryParameter(
                self._glo_samples_passed,  # type: ignore
                enums.QUERY_RESULT,
            )
        if self._primitives_enabled:
            self._ctx._gl.endQuery(enums.TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN)
            self._primitives = self._ctx._gl.getQueryParameter(
                self._glo_primitives_generated,  # type: ignore
                enums.QUERY_RESULT,
            )

    def delete(self):
        WebGLQuery.delete_glo(self._ctx, [self._glo_samples_passed, self._glo_primitives_generated])

    @staticmethod
    def delete_glo(ctx: WebGLContext, glos: list[JSWebGLQuery | None]):
        for glo in glos:
            ctx._gl.deleteQuery(glo)

        ctx.stats.decr("query")
