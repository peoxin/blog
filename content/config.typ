#let web-math(content) = {
  show math.equation.where(block: false): it => {
    if target() == "html" {
      html.span(role: "math", html.frame(it))
    } else {
      it
    }
  }

  show math.equation.where(block: true): it => {
    if target() == "html" {
      html.figure(role: "math", html.frame(it))
    } else {
      it
    }
  }

  content
}

#let web-link(content) = {
  // Open external links and non-web resources in a new tab
  show link: it => {
    if type(it.dest) == str {
      let is-external = it.dest.starts-with("http")
      let is-resource = it.dest.contains(".") and not it.dest.ends-with(".html")
      if is-external or is-resource {
        html.a(
          href: it.dest,
          target: "_blank",
          rel: ("noopener", "noreferrer"),
          it.body,
        )
      } else {
        it
      }
    } else {
      it
    }
  }

  content
}

#let web-font() = {
  html.link(rel: "stylesheet", href: "https://cdn.jsdelivr.net/npm/lxgw-wenkai-screen-web/style.min.css")
}

#let format-date(date) = {
  if type(date) == datetime {
    date.display()
  } else if type(date) == str {
    date
  } else {
    ""
  }
}

#let post(
  title: "",
  pub-date: none,
  mod-date: none,
  lang: "zh",
  content,
) = {
  show: web-math
  show: web-link

  set text(lang: lang)

  html.html(
    lang: lang,
    {
      html.head({
        html.meta(charset: "utf-8")
        html.meta(name: "viewport", content: "width=device-width, initial-scale=1")

        html.title(title)
        html.meta(name: "pub-date", content: format-date(pub-date))
        html.meta(name: "mod-date", content: format-date(mod-date))
        html.link(rel: "icon", href: "/assets/favicon.ico")

        web-font()

        let css-links = (
          "/assets/theme.css",
        )
        for css-link in css-links.dedup() {
          html.link(rel: "stylesheet", href: css-link)
        }

        let js-scripts = (
          "/assets/code-block.js",
          "/assets/toggle-font.js",
          "/assets/toggle-theme.js",
        )
        for js-src in js-scripts.dedup() {
          html.script(src: js-src)
        }
      })

      html.body({
        // Navigation bar
        let nav-links = (
          "/": "Home",
        )
        html.header(
          html.nav(
            for (href, title) in nav-links {
              html.a(href: href, title)
            },
          ),
        )

        let pub-date-elem = if format-date(pub-date) != "" {
          html.span(class: "pub-date", "Pub" + sym.dot + format-date(pub-date))
        } else {
          none
        }
        let mod-date-elem = if format-date(mod-date) != "" {
          html.span(class: "mod-date", "Mod" + sym.dot + format-date(mod-date))
        } else {
          none
        }
        html.article(
          content + html.div(class: "pub-mod-date", pub-date-elem + mod-date-elem)
        )

        html.footer([2026 #sym.copyright peoxin])
      })
    },
  )
}
