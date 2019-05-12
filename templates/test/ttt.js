!function (t, e) {
    var s = e.body, n = e.querySelector.bind(e), a = e.querySelectorAll.bind(e), o = n("html"), c = n("#gotop"),
        l = n("#menu"), r = n("#header"), d = n("#mask"), h = n("#menu-toggle"), f = n("#menu-off"), u = n("#loading"),
        m = t.requestAnimationFrame, v = 12, g = Array.prototype.forEach,
        p = "ontouchstart" in t && /Mobile|Android|iOS|iPhone|iPad|iPod|Windows Phone|KFAPWI/i.test(navigator.userAgent) ? "touchstart" : "click",
        L = /micromessenger/i.test(navigator.userAgent), y = function () {
        }, w = function (t) {
            var e = t.offsetLeft, i = t.offsetTop;
            if (t.offsetParent) {
                var s = arguments.callee(t.offsetParent);
                e += s.x, i += s.y
            }
            return {x: e, y: i}
        }, x = function () {
            return e.documentElement.scrollTop || e.body.scrollTop
        }, $ = {
            goTop: function (e) {
                var i = x(), s = arguments.length > 2 ? arguments[1] : Math.abs(i - e) / v;
                i && i > e ? (t.scrollTo(0, Math.max(i - s, 0)), m(arguments.callee.bind(this, e, s))) : e && e > i ? (t.scrollTo(0, Math.min(i + s, e)), m(arguments.callee.bind(this, e, s))) : this.toc.actived(e)
            }, hideOnMask: [], modal: function (t) {
                this.$modal = n(t), this.$off = this.$modal.querySelector(".close");
                var e = this;
                this.show = function () {
                    d.classList.add("in"), e.$modal.classList.add("ready"), setTimeout(function () {
                        e.$modal.classList.add("in")
                    }, 0)
                }, this.onHide = y, this.hide = function () {
                    e.onHide(), d.classList.remove("in"), e.$modal.classList.remove("in"), setTimeout(function () {
                        e.$modal.classList.remove("ready")
                    }, 300)
                }, this.toggle = function () {
                    return e.$modal.classList.contains("in") ? e.hide() : e.show()
                }, $.hideOnMask.push(this.hide), this.$off && this.$off.addEventListener(p, this.hide)
            }, share: function () {
                var t = n("#pageShare"), i = n("#shareFab"), s = new this.modal("#globalShare");
                n("#menuShare").addEventListener(p, s.toggle), i && (i.addEventListener(p, function () {
                    t.classList.toggle("in")
                }, !1), e.addEventListener(p, function (e) {
                    !i.contains(e.target) && t.classList.remove("in")
                }, !1));
                var o = new this.modal("#wxShare");
                o.onHide = s.hide, g.call(a(".wxFab"), function (t) {
                    t.addEventListener(p, o.toggle)
                })
            }, reward: function () {
                var t = new this.modal("#reward");
                n("#rewardBtn").addEventListener(p, t.toggle);
                var e = n("#rewardToggle"), i = n("#rewardCode");
                e && e.addEventListener("change", function () {
                    i.src = this.checked ? this.dataset.alipay : this.dataset.wechat
                })
            }
        };t.Waves ? (Waves.init(), Waves.attach(".global-share li", ["waves-block"]), Waves.attach(".article-tag-list-link, #page-nav a, #page-nav span", ["waves-button"])) : console.error("Waves loading failed.")
}(window, document);
