# A component takes data and returns markup

Components had started to read files through default props, read the environment, and build their
own hrefs. We decided that nothing under `src/components/` reads a file or the environment. Nothing
there builds a route. A component takes data and an `href` as props and returns markup. Only the app
layer calls a loader or a route builder. A test over the component tree enforces the rule. A breach
fails the build. A component may join a roster id or a week onto an href it was given, because it still knows no route root.
