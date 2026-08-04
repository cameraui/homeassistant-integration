//#region node_modules/@camera.ui/logger/dist/protocol-BB4jdtUC.js
var e = "__cuiLoggerState__";
function t() {
	let t = globalThis, n = t[e];
	return n || (n = {
		capacity: 600,
		entries: [],
		storeListeners: /* @__PURE__ */ new Set(),
		debugEnabled: !1,
		scopeOverrides: /* @__PURE__ */ new Map(),
		recording: !1,
		flagListeners: /* @__PURE__ */ new Set()
	}, t[e] = n), n;
}
function n(e, n) {
	let r = t();
	n ? r.scopeOverrides.set(n, e) : r.debugEnabled = e, c();
}
function r(e) {
	t().scopeOverrides.delete(e) && c();
}
function i(e) {
	let n = t();
	return e !== void 0 && n.scopeOverrides.has(e) ? n.scopeOverrides.get(e) : n.debugEnabled;
}
function a(e) {
	t().recording = e, c();
}
function o() {
	return t().recording;
}
function s(e) {
	let { flagListeners: n } = t();
	return n.add(e), () => {
		n.delete(e);
	};
}
function c() {
	let e = t();
	for (let t of e.flagListeners) try {
		t();
	} catch {}
}
function l(e) {
	return (console[e] ?? console.log).bind(console);
}
var u = {
	log: l("log"),
	debug: l("debug"),
	info: l("info"),
	warn: l("warn"),
	error: l("error")
};
function d(e) {
	t().capacity = Math.max(1, Math.floor(e)), g();
}
function f(e) {
	t().entries.push(e), g(), _();
}
function p() {
	return t().entries.slice();
}
function m() {
	t().entries = [], _();
}
function h(e) {
	let { storeListeners: n } = t();
	return n.add(e), () => {
		n.delete(e);
	};
}
function g() {
	let e = t();
	e.entries.length > e.capacity && e.entries.splice(0, e.entries.length - e.capacity);
}
function _() {
	let e = t();
	for (let t of e.storeListeners) try {
		t(e.entries);
	} catch {}
}
function v(e) {
	if (typeof e == "string") return e;
	if (e === void 0) return "undefined";
	if (e === null) return "null";
	if (e instanceof Error) return `${e.name}: ${e.message}${e.stack ? `\n${e.stack}` : ""}`;
	if (typeof e != "object") return String(e);
	try {
		let t = /* @__PURE__ */ new WeakSet();
		return JSON.stringify(e, (e, n) => {
			if (typeof n == "bigint") return `${n}n`;
			if (typeof n == "function") return `[Function ${n.name || "anonymous"}]`;
			if (typeof n == "object" && n) {
				if (t.has(n)) return "[Circular]";
				t.add(n);
			}
			return n;
		});
	} catch {
		try {
			return String(e);
		} catch {
			return "[Unserializable]";
		}
	}
}
var y = /%[sdifoOjc%]/g, b = /%[sdifoOjc]/;
function x(e) {
	let t = e[0];
	if (typeof t != "string" || !b.test(t)) return e.map(v).join(" ");
	let n = e.slice(1), r = 0, i = t.replace(y, (e) => {
		if (e === "%%") return "%";
		if (r >= n.length) return e;
		let t = n[r++];
		switch (e) {
			case "%s": return typeof t == "string" ? t : v(t);
			case "%d":
			case "%i": {
				let e = typeof t == "number" ? t : Number(t);
				return Number.isNaN(e) ? "NaN" : String(Math.trunc(e));
			}
			case "%f": {
				let e = typeof t == "number" ? t : Number(t);
				return Number.isNaN(e) ? "NaN" : String(e);
			}
			case "%c": return "";
			default: return v(t);
		}
	}), a = n.slice(r).map(v).join(" ");
	return a ? `${i} ${a}` : i;
}
function S(e, t = 2) {
	return String(e).padStart(t, "0");
}
function ee(e = Date.now()) {
	let t = new Date(e);
	return `${S(t.getHours())}:${S(t.getMinutes())}:${S(t.getSeconds())}.${S(t.getMilliseconds(), 3)}`;
}
var C = {
	debug: "debug",
	log: "log",
	info: "info",
	warn: "warn",
	error: "error"
}, w = class e {
	scope;
	constructor(e) {
		this.scope = e;
	}
	static scope(t) {
		return new e(t);
	}
	debug(...e) {
		this.emit("debug", e);
	}
	log(...e) {
		this.emit("log", e);
	}
	info(...e) {
		this.emit("info", e);
	}
	warn(...e) {
		this.emit("warn", e);
	}
	error(...e) {
		this.emit("error", e);
	}
	emit(e, t) {
		if (e === "debug" && !i(this.scope)) return;
		let n = `[${this.scope} ${ee()}]`;
		typeof t[0] == "string" ? u[C[e]](`${n} ${t[0]}`, ...t.slice(1)) : u[C[e]](n, ...t), o() && f({
			t: Date.now(),
			level: e,
			scope: this.scope,
			msg: x(t)
		});
	}
	static setDebug(e, t) {
		n(e, t);
	}
	static isDebug(e) {
		return i(e);
	}
	static clearScope(e) {
		r(e);
	}
	static setRecording(e) {
		a(e);
	}
	static isRecording() {
		return o();
	}
	static onChange(e) {
		return s(e);
	}
	static entries() {
		return p();
	}
	static clear() {
		m();
	}
	static onEntries(e) {
		return h(e);
	}
	static setCapacity(e) {
		d(e);
	}
};
//#endregion
//#region node_modules/@vue/shared/dist/shared.esm-bundler.js
// @__NO_SIDE_EFFECTS__
function T(e) {
	let t = /* @__PURE__ */ Object.create(null);
	for (let n of e.split(",")) t[n] = 1;
	return (e) => e in t;
}
var E = {}, te = [], D = () => {}, ne = () => !1, O = (e) => e.charCodeAt(0) === 111 && e.charCodeAt(1) === 110 && (e.charCodeAt(2) > 122 || e.charCodeAt(2) < 97), k = (e) => e.startsWith("onUpdate:"), A = Object.assign, re = (e, t) => {
	let n = e.indexOf(t);
	n > -1 && e.splice(n, 1);
}, ie = Object.prototype.hasOwnProperty, j = (e, t) => ie.call(e, t), M = Array.isArray, ae = (e) => de(e) === "[object Map]", oe = (e) => de(e) === "[object Set]", se = (e) => de(e) === "[object Date]", N = (e) => typeof e == "function", P = (e) => typeof e == "string", ce = (e) => typeof e == "symbol", F = (e) => typeof e == "object" && !!e, le = (e) => (F(e) || N(e)) && N(e.then) && N(e.catch), ue = Object.prototype.toString, de = (e) => ue.call(e), fe = (e) => de(e).slice(8, -1), pe = (e) => de(e) === "[object Object]", I = (e) => P(e) && e !== "NaN" && e[0] !== "-" && "" + parseInt(e, 10) === e, me = /* @__PURE__ */ T(",key,ref,ref_for,ref_key,onVnodeBeforeMount,onVnodeMounted,onVnodeBeforeUpdate,onVnodeUpdated,onVnodeBeforeUnmount,onVnodeUnmounted"), he = (e) => {
	let t = /* @__PURE__ */ Object.create(null);
	return ((n) => t[n] || (t[n] = e(n)));
}, ge = /-\w/g, L = he((e) => e.replace(ge, (e) => e.slice(1).toUpperCase())), _e = /\B([A-Z])/g, ve = he((e) => e.replace(_e, "-$1").toLowerCase()), ye = he((e) => e.charAt(0).toUpperCase() + e.slice(1)), be = he((e) => e ? `on${ye(e)}` : ""), xe = (e, t) => !Object.is(e, t), Se = (e, ...t) => {
	for (let n = 0; n < e.length; n++) e[n](...t);
}, Ce = (e, t, n, r = !1) => {
	Object.defineProperty(e, t, {
		configurable: !0,
		enumerable: !1,
		writable: r,
		value: n
	});
}, we = (e) => {
	let t = parseFloat(e);
	return isNaN(t) ? e : t;
}, Te, Ee = () => Te ||= typeof globalThis < "u" ? globalThis : typeof self < "u" ? self : typeof window < "u" ? window : typeof global < "u" ? global : {};
function De(e) {
	if (M(e)) {
		let t = {};
		for (let n = 0; n < e.length; n++) {
			let r = e[n], i = P(r) ? je(r) : De(r);
			if (i) for (let e in i) t[e] = i[e];
		}
		return t;
	}
	if (P(e) || F(e)) return e;
}
var Oe = /;(?![^(]*\))/g, ke = /:([^]+)/, Ae = /\/\*[^]*?\*\//g;
function je(e) {
	let t = {};
	return e.replace(Ae, "").split(Oe).forEach((e) => {
		if (e) {
			let n = e.split(ke);
			n.length > 1 && (t[n[0].trim()] = n[1].trim());
		}
	}), t;
}
function Me(e) {
	let t = "";
	if (P(e)) t = e;
	else if (M(e)) for (let n = 0; n < e.length; n++) {
		let r = Me(e[n]);
		r && (t += r + " ");
	}
	else if (F(e)) for (let n in e) e[n] && (t += n + " ");
	return t.trim();
}
var Ne = "itemscope,allowfullscreen,formnovalidate,ismap,nomodule,novalidate,readonly", Pe = /* @__PURE__ */ T(Ne);
Ne + "";
function Fe(e) {
	return !!e || e === "";
}
function Ie(e, t) {
	if (e.length !== t.length) return !1;
	let n = !0;
	for (let r = 0; n && r < e.length; r++) n = Le(e[r], t[r]);
	return n;
}
function Le(e, t) {
	if (e === t) return !0;
	let n = se(e), r = se(t);
	if (n || r) return n && r ? e.getTime() === t.getTime() : !1;
	if (n = ce(e), r = ce(t), n || r) return e === t;
	if (n = M(e), r = M(t), n || r) return n && r ? Ie(e, t) : !1;
	if (n = F(e), r = F(t), n || r) {
		if (!n || !r || Object.keys(e).length !== Object.keys(t).length) return !1;
		for (let n in e) {
			let r = e.hasOwnProperty(n), i = t.hasOwnProperty(n);
			if (r && !i || !r && i || !Le(e[n], t[n])) return !1;
		}
	}
	return String(e) === String(t);
}
var Re = (e) => !!(e && e.__v_isRef === !0), ze = (e) => P(e) ? e : e == null ? "" : M(e) || F(e) && (e.toString === ue || !N(e.toString)) ? Re(e) ? ze(e.value) : JSON.stringify(e, Be, 2) : String(e), Be = (e, t) => Re(t) ? Be(e, t.value) : ae(t) ? { [`Map(${t.size})`]: [...t.entries()].reduce((e, [t, n], r) => (e[Ve(t, r) + " =>"] = n, e), {}) } : oe(t) ? { [`Set(${t.size})`]: [...t.values()].map((e) => Ve(e)) } : ce(t) ? Ve(t) : F(t) && !M(t) && !pe(t) ? String(t) : t, Ve = (e, t = "") => ce(e) ? `Symbol(${e.description ?? t})` : e, R, He = class {
	constructor(e = !1) {
		this.detached = e, this._active = !0, this._on = 0, this.effects = [], this.cleanups = [], this._isPaused = !1, this._warnOnRun = !0, this.__v_skip = !0, !e && R && (R.active ? (this.parent = R, this.index = (R.scopes || (R.scopes = [])).push(this) - 1) : (this._active = !1, this._warnOnRun = !1));
	}
	get active() {
		return this._active;
	}
	pause() {
		if (this._active) {
			this._isPaused = !0;
			let e, t;
			if (this.scopes) {
				let n = this.scopes.slice();
				for (e = 0, t = n.length; e < t; e++) n[e].pause();
			}
			for (e = 0, t = this.effects.length; e < t; e++) this.effects[e].pause();
		}
	}
	resume() {
		if (this._active && this._isPaused) {
			this._isPaused = !1;
			let e, t;
			if (this.scopes) {
				let n = this.scopes.slice();
				for (e = 0, t = n.length; e < t; e++) n[e].resume();
			}
			let n = this.effects.slice();
			for (e = 0, t = n.length; e < t; e++) n[e].resume();
		}
	}
	run(e) {
		if (this._active) {
			let t = R;
			try {
				return R = this, e();
			} finally {
				R = t;
			}
		}
	}
	on() {
		++this._on === 1 && (this.prevScope = R, R = this);
	}
	off() {
		if (this._on > 0 && --this._on === 0) {
			if (R === this) R = this.prevScope;
			else {
				let e = R;
				for (; e;) {
					if (e.prevScope === this) {
						e.prevScope = this.prevScope;
						break;
					}
					e = e.prevScope;
				}
			}
			this.prevScope = void 0;
		}
	}
	stop(e) {
		if (this._active) {
			this._active = !1;
			let t, n;
			for (t = 0, n = this.effects.length; t < n; t++) this.effects[t].stop();
			for (this.effects.length = 0, t = 0, n = this.cleanups.length; t < n; t++) this.cleanups[t]();
			if (this.cleanups.length = 0, this.scopes) {
				let e = this.scopes.slice();
				for (t = 0, n = e.length; t < n; t++) e[t].stop(!0);
				this.scopes.length = 0;
			}
			if (!this.detached && this.parent && !e) {
				let e = this.parent.scopes.pop();
				e && e !== this && (this.parent.scopes[this.index] = e, e.index = this.index);
			}
			this.parent = void 0;
		}
	}
};
function Ue(e) {
	return new He(e);
}
function We() {
	return R;
}
function Ge(e, t = !1) {
	R && R.cleanups.push(e);
}
var z, Ke = /* @__PURE__ */ new WeakSet(), qe = class {
	constructor(e) {
		this.fn = e, this.deps = void 0, this.depsTail = void 0, this.flags = 5, this.next = void 0, this.cleanup = void 0, this.scheduler = void 0, R && (R.active ? R.effects.push(this) : this.flags &= -2);
	}
	pause() {
		this.flags |= 64;
	}
	resume() {
		this.flags & 64 && (this.flags &= -65, Ke.has(this) && (Ke.delete(this), this.trigger()));
	}
	notify() {
		this.flags & 2 && !(this.flags & 32) || this.flags & 8 || Ze(this);
	}
	run() {
		if (!(this.flags & 1)) return this.fn();
		this.flags |= 2, ut(this), et(this);
		let e = z, t = ot;
		z = this, ot = !0;
		try {
			return this.fn();
		} finally {
			tt(this), z = e, ot = t, this.flags &= -3;
		}
	}
	stop() {
		if (this.flags & 1) {
			for (let e = this.deps; e; e = e.nextDep) it(e);
			this.deps = this.depsTail = void 0, ut(this), this.onStop && this.onStop(), this.flags &= -2;
		}
	}
	trigger() {
		this.flags & 64 ? Ke.add(this) : this.scheduler ? this.scheduler() : this.runIfDirty();
	}
	runIfDirty() {
		nt(this) && this.run();
	}
	get dirty() {
		return nt(this);
	}
}, Je = 0, Ye, Xe;
function Ze(e, t = !1) {
	if (e.flags |= 8, t) {
		e.next = Xe, Xe = e;
		return;
	}
	e.next = Ye, Ye = e;
}
function Qe() {
	Je++;
}
function $e() {
	if (--Je > 0) return;
	if (Xe) {
		let e = Xe;
		for (Xe = void 0; e;) {
			let t = e.next;
			e.next = void 0, e.flags &= -9, e = t;
		}
	}
	let e;
	for (; Ye;) {
		let t = Ye;
		for (Ye = void 0; t;) {
			let n = t.next;
			if (t.next = void 0, t.flags &= -9, t.flags & 1) try {
				t.trigger();
			} catch (t) {
				e ||= t;
			}
			t = n;
		}
	}
	if (e) throw e;
}
function et(e) {
	for (let t = e.deps; t; t = t.nextDep) t.version = -1, t.prevActiveLink = t.dep.activeLink, t.dep.activeLink = t;
}
function tt(e) {
	let t, n = e.depsTail, r = n;
	for (; r;) {
		let e = r.prevDep;
		r.version === -1 ? (r === n && (n = e), it(r), at(r)) : t = r, r.dep.activeLink = r.prevActiveLink, r.prevActiveLink = void 0, r = e;
	}
	e.deps = t, e.depsTail = n;
}
function nt(e) {
	for (let t = e.deps; t; t = t.nextDep) if (t.dep.version !== t.version || t.dep.computed && (rt(t.dep.computed) || t.dep.version !== t.version)) return !0;
	return !!e._dirty;
}
function rt(e) {
	if (e.flags & 4 && !(e.flags & 16) || (e.flags &= -17, e.globalVersion === dt) || (e.globalVersion = dt, !e.isSSR && e.flags & 128 && (!e.deps && !e._dirty || !nt(e)))) return;
	e.flags |= 2;
	let t = e.dep, n = z, r = ot;
	z = e, ot = !0;
	try {
		et(e);
		let n = e.fn(e._value);
		(t.version === 0 || xe(n, e._value)) && (e.flags |= 128, e._value = n, t.version++);
	} catch (e) {
		throw t.version++, e;
	} finally {
		z = n, ot = r, tt(e), e.flags &= -3;
	}
}
function it(e, t = !1) {
	let { dep: n, prevSub: r, nextSub: i } = e;
	if (r && (r.nextSub = i, e.prevSub = void 0), i && (i.prevSub = r, e.nextSub = void 0), n.subs === e && (n.subs = r, !r && n.computed)) {
		n.computed.flags &= -5;
		for (let e = n.computed.deps; e; e = e.nextDep) it(e, !0);
	}
	!t && !--n.sc && n.map && n.map.delete(n.key);
}
function at(e) {
	let { prevDep: t, nextDep: n } = e;
	t && (t.nextDep = n, e.prevDep = void 0), n && (n.prevDep = t, e.nextDep = void 0);
}
var ot = !0, st = [];
function ct() {
	st.push(ot), ot = !1;
}
function lt() {
	let e = st.pop();
	ot = e === void 0 || e;
}
function ut(e) {
	let { cleanup: t } = e;
	if (e.cleanup = void 0, t) {
		let e = z;
		z = void 0;
		try {
			t();
		} finally {
			z = e;
		}
	}
}
var dt = 0, ft = class {
	constructor(e, t) {
		this.sub = e, this.dep = t, this.version = t.version, this.nextDep = this.prevDep = this.nextSub = this.prevSub = this.prevActiveLink = void 0;
	}
}, pt = class {
	constructor(e) {
		this.computed = e, this.version = 0, this.activeLink = void 0, this.subs = void 0, this.map = void 0, this.key = void 0, this.sc = 0, this.__v_skip = !0;
	}
	track(e) {
		if (!z || !ot || z === this.computed) return;
		let t = this.activeLink;
		if (t === void 0 || t.sub !== z) t = this.activeLink = new ft(z, this), z.deps ? (t.prevDep = z.depsTail, z.depsTail.nextDep = t, z.depsTail = t) : z.deps = z.depsTail = t, mt(t);
		else if (t.version === -1 && (t.version = this.version, t.nextDep)) {
			let e = t.nextDep;
			e.prevDep = t.prevDep, t.prevDep && (t.prevDep.nextDep = e), t.prevDep = z.depsTail, t.nextDep = void 0, z.depsTail.nextDep = t, z.depsTail = t, z.deps === t && (z.deps = e);
		}
		return t;
	}
	trigger(e) {
		this.version++, dt++, this.notify(e);
	}
	notify(e) {
		Qe();
		try {
			for (let e = this.subs; e; e = e.prevSub) e.sub.notify() && e.sub.dep.notify();
		} finally {
			$e();
		}
	}
};
function mt(e) {
	if (e.dep.sc++, e.sub.flags & 4) {
		let t = e.dep.computed;
		if (t && !e.dep.subs) {
			t.flags |= 20;
			for (let e = t.deps; e; e = e.nextDep) mt(e);
		}
		let n = e.dep.subs;
		n !== e && (e.prevSub = n, n && (n.nextSub = e)), e.dep.subs = e;
	}
}
var ht = /* @__PURE__ */ new WeakMap(), gt = /* @__PURE__ */ Symbol(""), _t = /* @__PURE__ */ Symbol(""), vt = /* @__PURE__ */ Symbol("");
function yt(e, t, n) {
	if (ot && z) {
		let t = ht.get(e);
		t || ht.set(e, t = /* @__PURE__ */ new Map());
		let r = t.get(n);
		r || (t.set(n, r = new pt()), r.map = t, r.key = n), r.track();
	}
}
function bt(e, t, n, r, i, a) {
	let o = ht.get(e);
	if (!o) {
		dt++;
		return;
	}
	let s = (e) => {
		e && e.trigger();
	};
	if (Qe(), t === "clear") o.forEach(s);
	else {
		let i = M(e), a = i && I(n);
		if (i && n === "length") {
			let e = Number(r);
			o.forEach((t, n) => {
				(n === "length" || n === vt || !ce(n) && n >= e) && s(t);
			});
		} else switch ((n !== void 0 || o.has(void 0)) && s(o.get(n)), a && s(o.get(vt)), t) {
			case "add":
				i ? a && s(o.get("length")) : (s(o.get(gt)), ae(e) && s(o.get(_t)));
				break;
			case "delete":
				i || (s(o.get(gt)), ae(e) && s(o.get(_t)));
				break;
			case "set": ae(e) && s(o.get(gt));
		}
	}
	$e();
}
function xt(e) {
	let t = /* @__PURE__ */ B(e);
	return t === e ? t : (yt(t, "iterate", vt), /* @__PURE__ */ un(e) ? t : t.map(pn));
}
function St(e) {
	return yt(e = /* @__PURE__ */ B(e), "iterate", vt), e;
}
function Ct(e, t) {
	return /* @__PURE__ */ ln(e) ? mn(/* @__PURE__ */ cn(e) ? pn(t) : t) : pn(t);
}
var wt = {
	__proto__: null,
	[Symbol.iterator]() {
		return Tt(this, Symbol.iterator, (e) => Ct(this, e));
	},
	concat(...e) {
		return xt(this).concat(...e.map((e) => M(e) ? xt(e) : e));
	},
	entries() {
		return Tt(this, "entries", (e) => (e[1] = Ct(this, e[1]), e));
	},
	every(e, t) {
		return Dt(this, "every", e, t, void 0, arguments);
	},
	filter(e, t) {
		return Dt(this, "filter", e, t, (e) => e.map((e) => Ct(this, e)), arguments);
	},
	find(e, t) {
		return Dt(this, "find", e, t, (e) => Ct(this, e), arguments);
	},
	findIndex(e, t) {
		return Dt(this, "findIndex", e, t, void 0, arguments);
	},
	findLast(e, t) {
		return Dt(this, "findLast", e, t, (e) => Ct(this, e), arguments);
	},
	findLastIndex(e, t) {
		return Dt(this, "findLastIndex", e, t, void 0, arguments);
	},
	forEach(e, t) {
		return Dt(this, "forEach", e, t, void 0, arguments);
	},
	includes(...e) {
		return kt(this, "includes", e);
	},
	indexOf(...e) {
		return kt(this, "indexOf", e);
	},
	join(e) {
		return xt(this).join(e);
	},
	lastIndexOf(...e) {
		return kt(this, "lastIndexOf", e);
	},
	map(e, t) {
		return Dt(this, "map", e, t, void 0, arguments);
	},
	pop() {
		return At(this, "pop");
	},
	push(...e) {
		return At(this, "push", e);
	},
	reduce(e, ...t) {
		return Ot(this, "reduce", e, t);
	},
	reduceRight(e, ...t) {
		return Ot(this, "reduceRight", e, t);
	},
	shift() {
		return At(this, "shift");
	},
	some(e, t) {
		return Dt(this, "some", e, t, void 0, arguments);
	},
	splice(...e) {
		return At(this, "splice", e);
	},
	toReversed() {
		return xt(this).toReversed();
	},
	toSorted(e) {
		return xt(this).toSorted(e);
	},
	toSpliced(...e) {
		return xt(this).toSpliced(...e);
	},
	unshift(...e) {
		return At(this, "unshift", e);
	},
	values() {
		return Tt(this, "values", (e) => Ct(this, e));
	}
};
function Tt(e, t, n) {
	let r = St(e), i = r[t]();
	return r !== e && !/* @__PURE__ */ un(e) && (i._next = i.next, i.next = () => {
		let e = i._next();
		return e.done || (e.value = n(e.value)), e;
	}), i;
}
var Et = Array.prototype;
function Dt(e, t, n, r, i, a) {
	let o = St(e), s = o !== e && !/* @__PURE__ */ un(e), c = o[t];
	if (c !== Et[t]) {
		let t = c.apply(e, a);
		return s ? pn(t) : t;
	}
	let l = n;
	o !== e && (s ? l = function(t, r) {
		return n.call(this, Ct(e, t), r, e);
	} : n.length > 2 && (l = function(t, r) {
		return n.call(this, t, r, e);
	}));
	let u = c.call(o, l, r);
	return s && i ? i(u) : u;
}
function Ot(e, t, n, r) {
	let i = St(e), a = i !== e && !/* @__PURE__ */ un(e), o = n, s = !1;
	i !== e && (a ? (s = r.length === 0, o = function(t, r, i) {
		return s && (s = !1, t = Ct(e, t)), n.call(this, t, Ct(e, r), i, e);
	}) : n.length > 3 && (o = function(t, r, i) {
		return n.call(this, t, r, i, e);
	}));
	let c = i[t](o, ...r);
	return s ? Ct(e, c) : c;
}
function kt(e, t, n) {
	let r = /* @__PURE__ */ B(e);
	yt(r, "iterate", vt);
	let i = r[t](...n);
	return (i === -1 || i === !1) && /* @__PURE__ */ dn(n[0]) ? (n[0] = /* @__PURE__ */ B(n[0]), r[t](...n)) : i;
}
function At(e, t, n = []) {
	ct(), Qe();
	let r = (/* @__PURE__ */ B(e))[t].apply(e, n);
	return $e(), lt(), r;
}
var jt = /* @__PURE__ */ T("__proto__,__v_isRef,__isVue"), Mt = new Set(/* @__PURE__ */ Object.getOwnPropertyNames(Symbol).filter((e) => e !== "arguments" && e !== "caller").map((e) => Symbol[e]).filter(ce));
function Nt(e) {
	ce(e) || (e = String(e));
	let t = /* @__PURE__ */ B(this);
	return yt(t, "has", e), t.hasOwnProperty(e);
}
var Pt = class {
	constructor(e = !1, t = !1) {
		this._isReadonly = e, this._isShallow = t;
	}
	get(e, t, n) {
		if (t === "__v_skip") return e.__v_skip;
		let r = this._isReadonly, i = this._isShallow;
		if (t === "__v_isReactive") return !r;
		if (t === "__v_isReadonly") return r;
		if (t === "__v_isShallow") return i;
		if (t === "__v_raw") return n === (r ? i ? en : $t : i ? Qt : Zt).get(e) || Object.getPrototypeOf(e) === Object.getPrototypeOf(n) ? e : void 0;
		let a = M(e);
		if (!r) {
			let e;
			if (a && (e = wt[t])) return e;
			if (t === "hasOwnProperty") return Nt;
		}
		let o = Reflect.get(e, t, /* @__PURE__ */ hn(e) ? e : n);
		if ((ce(t) ? Mt.has(t) : jt(t)) || (r || yt(e, "get", t), i)) return o;
		if (/* @__PURE__ */ hn(o)) {
			let e = a && I(t) ? o : o.value;
			return r && F(e) ? /* @__PURE__ */ an(e) : e;
		}
		return F(o) ? r ? /* @__PURE__ */ an(o) : /* @__PURE__ */ nn(o) : o;
	}
}, Ft = class extends Pt {
	constructor(e = !1) {
		super(!1, e);
	}
	set(e, t, n, r) {
		let i = e[t], a = M(e) && I(t);
		if (!this._isShallow) {
			let e = /* @__PURE__ */ ln(i);
			if (!/* @__PURE__ */ un(n) && !/* @__PURE__ */ ln(n) && (i = /* @__PURE__ */ B(i), n = /* @__PURE__ */ B(n)), !a && /* @__PURE__ */ hn(i) && !/* @__PURE__ */ hn(n)) return e || (i.value = n), !0;
		}
		let o = a ? Number(t) < e.length : j(e, t), s = Reflect.set(e, t, n, /* @__PURE__ */ hn(e) ? e : r);
		return e === /* @__PURE__ */ B(r) && s && (o ? xe(n, i) && bt(e, "set", t, n, i) : bt(e, "add", t, n)), s;
	}
	deleteProperty(e, t) {
		let n = j(e, t), r = e[t], i = Reflect.deleteProperty(e, t);
		return i && n && bt(e, "delete", t, void 0, r), i;
	}
	has(e, t) {
		let n = Reflect.has(e, t);
		return (!ce(t) || !Mt.has(t)) && yt(e, "has", t), n;
	}
	ownKeys(e) {
		return yt(e, "iterate", M(e) ? "length" : gt), Reflect.ownKeys(e);
	}
}, It = class extends Pt {
	constructor(e = !1) {
		super(!0, e);
	}
	set(e, t) {
		return !0;
	}
	deleteProperty(e, t) {
		return !0;
	}
}, Lt = /* @__PURE__ */ new Ft(), Rt = /* @__PURE__ */ new It(), zt = /* @__PURE__ */ new Ft(!0), Bt = /* @__PURE__ */ new It(!0), Vt = (e) => e, Ht = (e) => Reflect.getPrototypeOf(e);
function Ut(e, t, n) {
	return function(...r) {
		let i = this.__v_raw, a = /* @__PURE__ */ B(i), o = ae(a), s = e === "entries" || e === Symbol.iterator && o, c = e === "keys" && o, l = i[e](...r), u = n ? Vt : t ? mn : pn;
		return !t && yt(a, "iterate", c ? _t : gt), A(Object.create(l), { next() {
			let { value: e, done: t } = l.next();
			return t ? {
				value: e,
				done: t
			} : {
				value: s ? [u(e[0]), u(e[1])] : u(e),
				done: t
			};
		} });
	};
}
function Wt(e) {
	return function(...t) {
		return e === "delete" ? !1 : e === "clear" ? void 0 : this;
	};
}
function Gt(e, t) {
	let n = {
		get(n) {
			let r = this.__v_raw, i = /* @__PURE__ */ B(r), a = /* @__PURE__ */ B(n);
			e || (xe(n, a) && yt(i, "get", n), yt(i, "get", a));
			let { has: o } = Ht(i), s = t ? Vt : e ? mn : pn;
			if (o.call(i, n)) return s(r.get(n));
			if (o.call(i, a)) return s(r.get(a));
			r !== i && r.get(n);
		},
		get size() {
			let t = this.__v_raw;
			return !e && yt(/* @__PURE__ */ B(t), "iterate", gt), t.size;
		},
		has(t) {
			let n = this.__v_raw, r = /* @__PURE__ */ B(n), i = /* @__PURE__ */ B(t);
			return e || (xe(t, i) && yt(r, "has", t), yt(r, "has", i)), t === i ? n.has(t) : n.has(t) || n.has(i);
		},
		forEach(n, r) {
			let i = this, a = i.__v_raw, o = /* @__PURE__ */ B(a), s = t ? Vt : e ? mn : pn;
			return !e && yt(o, "iterate", gt), a.forEach((e, t) => n.call(r, s(e), s(t), i));
		}
	};
	return A(n, e ? {
		add: Wt("add"),
		set: Wt("set"),
		delete: Wt("delete"),
		clear: Wt("clear")
	} : {
		add(e) {
			let n = /* @__PURE__ */ B(this), r = Ht(n), i = /* @__PURE__ */ B(e), a = !t && !/* @__PURE__ */ un(e) && !/* @__PURE__ */ ln(e) ? i : e;
			return r.has.call(n, a) || xe(e, a) && r.has.call(n, e) || xe(i, a) && r.has.call(n, i) || (n.add(a), bt(n, "add", a, a)), this;
		},
		set(e, n) {
			!t && !/* @__PURE__ */ un(n) && !/* @__PURE__ */ ln(n) && (n = /* @__PURE__ */ B(n));
			let r = /* @__PURE__ */ B(this), { has: i, get: a } = Ht(r), o = i.call(r, e);
			o ||= (e = /* @__PURE__ */ B(e), i.call(r, e));
			let s = a.call(r, e);
			return r.set(e, n), o ? xe(n, s) && bt(r, "set", e, n, s) : bt(r, "add", e, n), this;
		},
		delete(e) {
			let t = /* @__PURE__ */ B(this), { has: n, get: r } = Ht(t), i = n.call(t, e);
			i ||= (e = /* @__PURE__ */ B(e), n.call(t, e));
			let a = r ? r.call(t, e) : void 0, o = t.delete(e);
			return i && bt(t, "delete", e, void 0, a), o;
		},
		clear() {
			let e = /* @__PURE__ */ B(this), t = e.size !== 0, n = e.clear();
			return t && bt(e, "clear", void 0, void 0, void 0), n;
		}
	}), [
		"keys",
		"values",
		"entries",
		Symbol.iterator
	].forEach((r) => {
		n[r] = Ut(r, e, t);
	}), n;
}
function Kt(e, t) {
	let n = Gt(e, t);
	return (t, r, i) => r === "__v_isReactive" ? !e : r === "__v_isReadonly" ? e : r === "__v_raw" ? t : Reflect.get(j(n, r) && r in t ? n : t, r, i);
}
var qt = { get: /* @__PURE__ */ Kt(!1, !1) }, Jt = { get: /* @__PURE__ */ Kt(!1, !0) }, Yt = { get: /* @__PURE__ */ Kt(!0, !1) }, Xt = { get: /* @__PURE__ */ Kt(!0, !0) }, Zt = /* @__PURE__ */ new WeakMap(), Qt = /* @__PURE__ */ new WeakMap(), $t = /* @__PURE__ */ new WeakMap(), en = /* @__PURE__ */ new WeakMap();
function tn(e) {
	switch (e) {
		case "Object":
		case "Array": return 1;
		case "Map":
		case "Set":
		case "WeakMap":
		case "WeakSet": return 2;
		default: return 0;
	}
}
// @__NO_SIDE_EFFECTS__
function nn(e) {
	return /* @__PURE__ */ ln(e) ? e : sn(e, !1, Lt, qt, Zt);
}
// @__NO_SIDE_EFFECTS__
function rn(e) {
	return sn(e, !1, zt, Jt, Qt);
}
// @__NO_SIDE_EFFECTS__
function an(e) {
	return sn(e, !0, Rt, Yt, $t);
}
// @__NO_SIDE_EFFECTS__
function on(e) {
	return sn(e, !0, Bt, Xt, en);
}
function sn(e, t, n, r, i) {
	if (!F(e) || e.__v_raw && !(t && e.__v_isReactive) || e.__v_skip || !Object.isExtensible(e)) return e;
	let a = i.get(e);
	if (a) return a;
	let o = tn(fe(e));
	if (o === 0) return e;
	let s = new Proxy(e, o === 2 ? r : n);
	return i.set(e, s), s;
}
// @__NO_SIDE_EFFECTS__
function cn(e) {
	return /* @__PURE__ */ ln(e) ? /* @__PURE__ */ cn(e.__v_raw) : !!(e && e.__v_isReactive);
}
// @__NO_SIDE_EFFECTS__
function ln(e) {
	return !!(e && e.__v_isReadonly);
}
// @__NO_SIDE_EFFECTS__
function un(e) {
	return !!(e && e.__v_isShallow);
}
// @__NO_SIDE_EFFECTS__
function dn(e) {
	return e ? !!e.__v_raw : !1;
}
// @__NO_SIDE_EFFECTS__
function B(e) {
	let t = e && e.__v_raw;
	return t ? /* @__PURE__ */ B(t) : e;
}
function fn(e) {
	return !j(e, "__v_skip") && Object.isExtensible(e) && Ce(e, "__v_skip", !0), e;
}
var pn = (e) => F(e) ? /* @__PURE__ */ nn(e) : e, mn = (e) => F(e) ? /* @__PURE__ */ an(e) : e;
// @__NO_SIDE_EFFECTS__
function hn(e) {
	return e ? e.__v_isRef === !0 : !1;
}
// @__NO_SIDE_EFFECTS__
function V(e) {
	return gn(e, !1);
}
// @__NO_SIDE_EFFECTS__
function H(e) {
	return gn(e, !0);
}
function gn(e, t) {
	return /* @__PURE__ */ hn(e) ? e : new _n(e, t);
}
var _n = class {
	constructor(e, t) {
		this.dep = new pt(), this.__v_isRef = !0, this.__v_isShallow = !1, this._rawValue = t ? e : /* @__PURE__ */ B(e), this._value = t ? e : pn(e), this.__v_isShallow = t;
	}
	get value() {
		return this.dep.track(), this._value;
	}
	set value(e) {
		let t = this._rawValue, n = this.__v_isShallow || /* @__PURE__ */ un(e) || /* @__PURE__ */ ln(e);
		e = n ? e : /* @__PURE__ */ B(e), xe(e, t) && (this._rawValue = e, this._value = n ? e : pn(e), this.dep.trigger());
	}
};
function U(e) {
	return /* @__PURE__ */ hn(e) ? e.value : e;
}
function W(e) {
	return N(e) ? e() : U(e);
}
var vn = {
	get: (e, t, n) => t === "__v_raw" ? e : U(Reflect.get(e, t, n)),
	set: (e, t, n, r) => {
		let i = e[t];
		return /* @__PURE__ */ hn(i) && !/* @__PURE__ */ hn(n) ? (i.value = n, !0) : Reflect.set(e, t, n, r);
	}
};
function yn(e) {
	return /* @__PURE__ */ cn(e) ? e : new Proxy(e, vn);
}
var bn = class {
	constructor(e, t, n) {
		this.fn = e, this.setter = t, this._value = void 0, this.dep = new pt(this), this.__v_isRef = !0, this.deps = void 0, this.depsTail = void 0, this.flags = 16, this.globalVersion = dt - 1, this.next = void 0, this.effect = this, this.__v_isReadonly = !t, this.isSSR = n;
	}
	notify() {
		if (this.flags |= 16, !(this.flags & 8) && z !== this) return Ze(this, !0), !0;
	}
	get value() {
		let e = this.dep.track();
		return rt(this), e && (e.version = this.dep.version), this._value;
	}
	set value(e) {
		this.setter && this.setter(e);
	}
};
// @__NO_SIDE_EFFECTS__
function xn(e, t, n = !1) {
	let r, i;
	return N(e) ? r = e : (r = e.get, i = e.set), new bn(r, i, n);
}
var Sn = {}, Cn = /* @__PURE__ */ new WeakMap(), wn = void 0;
function Tn(e, t = !1, n = wn) {
	if (n) {
		let t = Cn.get(n);
		t || Cn.set(n, t = []), t.push(e);
	}
}
function En(e, t, n = E) {
	let { immediate: r, deep: i, once: a, scheduler: o, augmentJob: s, call: c } = n, l = (e) => i ? e : /* @__PURE__ */ un(e) || i === !1 || i === 0 ? Dn(e, 1) : Dn(e), u, d, f, p, m = !1, h = !1;
	if (/* @__PURE__ */ hn(e) ? (d = () => e.value, m = /* @__PURE__ */ un(e)) : /* @__PURE__ */ cn(e) ? (d = () => l(e), m = !0) : M(e) ? (h = !0, m = e.some((e) => /* @__PURE__ */ cn(e) || /* @__PURE__ */ un(e)), d = () => e.map((e) => {
		if (/* @__PURE__ */ hn(e)) return e.value;
		if (/* @__PURE__ */ cn(e)) return l(e);
		if (N(e)) return c ? c(e, 2) : e();
	})) : d = N(e) ? t ? c ? () => c(e, 2) : e : () => {
		if (f) {
			ct();
			try {
				f();
			} finally {
				lt();
			}
		}
		let t = wn;
		wn = u;
		try {
			return c ? c(e, 3, [p]) : e(p);
		} finally {
			wn = t;
		}
	} : D, t && i) {
		let e = d, t = i === !0 ? Infinity : i;
		d = () => Dn(e(), t);
	}
	let g = We(), _ = () => {
		u.stop(), g && g.active && re(g.effects, u);
	};
	if (a && t) {
		let e = t;
		t = (...t) => {
			let n = e(...t);
			return _(), n;
		};
	}
	let v = h ? Array(e.length).fill(Sn) : Sn, y = (e) => {
		if (!(!(u.flags & 1) || !u.dirty && !e)) if (t) {
			let n = u.run();
			if (e || i || m || (h ? n.some((e, t) => xe(e, v[t])) : xe(n, v))) {
				f && f();
				let e = wn;
				wn = u;
				try {
					let e = [
						n,
						v === Sn ? void 0 : h && v[0] === Sn ? [] : v,
						p
					];
					v = n, c ? c(t, 3, e) : t(...e);
				} finally {
					wn = e;
				}
			}
		} else u.run();
	};
	return s && s(y), u = new qe(d), u.scheduler = o ? () => o(y, !1) : y, p = (e) => Tn(e, !1, u), f = u.onStop = () => {
		let e = Cn.get(u);
		if (e) {
			if (c) c(e, 4);
			else for (let t of e) t();
			Cn.delete(u);
		}
	}, t ? r ? y(!0) : v = u.run() : o ? o(y.bind(null, !0), !0) : u.run(), _.pause = u.pause.bind(u), _.resume = u.resume.bind(u), _.stop = _, _;
}
function Dn(e, t = Infinity, n) {
	if (t <= 0 || !F(e) || e.__v_skip || (n ||= /* @__PURE__ */ new Map(), (n.get(e) || 0) >= t)) return e;
	if (n.set(e, t), t--, /* @__PURE__ */ hn(e)) Dn(e.value, t, n);
	else if (M(e)) for (let r = 0; r < e.length; r++) Dn(e[r], t, n);
	else if (oe(e) || ae(e)) e.forEach((e) => {
		Dn(e, t, n);
	});
	else if (pe(e)) {
		for (let r in e) Dn(e[r], t, n);
		for (let r of Object.getOwnPropertySymbols(e)) Object.prototype.propertyIsEnumerable.call(e, r) && Dn(e[r], t, n);
	}
	return e;
}
//#endregion
//#region node_modules/@vue/runtime-core/dist/runtime-core.esm-bundler.js
function On(e, t, n, r) {
	try {
		return r ? e(...r) : e();
	} catch (e) {
		An(e, t, n);
	}
}
function kn(e, t, n, r) {
	if (N(e)) {
		let i = On(e, t, n, r);
		return i && le(i) && i.catch((e) => {
			An(e, t, n);
		}), i;
	}
	if (M(e)) {
		let i = [];
		for (let a = 0; a < e.length; a++) i.push(kn(e[a], t, n, r));
		return i;
	}
}
function An(e, t, n, r = !0) {
	let i = t ? t.vnode : null, { errorHandler: a, throwUnhandledErrorInProduction: o } = t && t.appContext.config || E;
	if (t) {
		let r = t.parent, i = t.proxy, o = `https://vuejs.org/error-reference/#runtime-${n}`;
		for (; r;) {
			let t = r.ec;
			if (t) {
				for (let n = 0; n < t.length; n++) if (t[n](e, i, o) === !1) return;
			}
			r = r.parent;
		}
		if (a) {
			ct(), On(a, null, 10, [
				e,
				i,
				o
			]), lt();
			return;
		}
	}
	jn(e, n, i, r, o);
}
function jn(e, t, n, r = !0, i = !1) {
	if (i) throw e;
	console.error(e);
}
var Mn = [], Nn = -1, Pn = [], Fn = null, In = 0, Ln = /* @__PURE__ */ Promise.resolve(), Rn = null;
function zn(e) {
	let t = Rn || Ln;
	return e ? t.then(this ? e.bind(this) : e) : t;
}
function Bn(e) {
	let t = Nn + 1, n = Mn.length;
	for (; t < n;) {
		let r = t + n >>> 1, i = Mn[r], a = Kn(i);
		a < e || a === e && i.flags & 2 ? t = r + 1 : n = r;
	}
	return t;
}
function Vn(e) {
	if (!(e.flags & 1)) {
		let t = Kn(e), n = Mn[Mn.length - 1];
		!n || !(e.flags & 2) && t >= Kn(n) ? Mn.push(e) : Mn.splice(Bn(t), 0, e), e.flags |= 1, Hn();
	}
}
function Hn() {
	Rn ||= Ln.then(qn);
}
function Un(e) {
	M(e) ? Pn.push(...e) : Fn && e.id === -1 ? Fn.splice(In + 1, 0, e) : e.flags & 1 || (Pn.push(e), e.flags |= 1), Hn();
}
function Wn(e, t, n = Nn + 1) {
	for (; n < Mn.length; n++) {
		let t = Mn[n];
		if (t && t.flags & 2) {
			if (e && t.id !== e.uid) continue;
			Mn.splice(n, 1), n--, t.flags & 4 && (t.flags &= -2), t(), t.flags & 4 || (t.flags &= -2);
		}
	}
}
function Gn(e) {
	if (Pn.length) {
		let e = [...new Set(Pn)].sort((e, t) => Kn(e) - Kn(t));
		if (Pn.length = 0, Fn) {
			Fn.push(...e);
			return;
		}
		for (Fn = e, In = 0; In < Fn.length; In++) {
			let e = Fn[In];
			e.flags & 4 && (e.flags &= -2), e.flags & 8 || e(), e.flags &= -2;
		}
		Fn = null, In = 0;
	}
}
var Kn = (e) => e.id == null ? e.flags & 2 ? -1 : Infinity : e.id;
function qn(e) {
	try {
		for (Nn = 0; Nn < Mn.length; Nn++) {
			let e = Mn[Nn];
			e && !(e.flags & 8) && (e.flags & 4 && (e.flags &= -2), On(e, e.i, e.i ? 15 : 14), e.flags & 4 || (e.flags &= -2));
		}
	} finally {
		for (; Nn < Mn.length; Nn++) {
			let e = Mn[Nn];
			e && (e.flags &= -2);
		}
		Nn = -1, Mn.length = 0, Gn(e), Rn = null, (Mn.length || Pn.length) && qn(e);
	}
}
var Jn = null, Yn = null;
function Xn(e) {
	let t = Jn;
	return Jn = e, Yn = e && e.type.__scopeId || null, t;
}
function Zn(e, t = Jn, n) {
	if (!t || e._n) return e;
	let r = (...n) => {
		r._d && aa(-1);
		let i = Xn(t), a = ta.length, o;
		try {
			o = e(...n);
		} finally {
			for (let e = ta.length; e > a; e--) ra();
			Xn(i), r._d && aa(1);
		}
		return o;
	};
	return r._n = !0, r._c = !0, r._d = !0, r;
}
function Qn(e, t, n, r) {
	let i = e.dirs, a = t && t.dirs;
	for (let o = 0; o < i.length; o++) {
		let s = i[o];
		a && (s.oldValue = a[o].value);
		let c = s.dir[r];
		c && (ct(), kn(c, n, 8, [
			e.el,
			s,
			e,
			t
		]), lt());
	}
}
function $n(e, t) {
	if (Ea) {
		let n = Ea.provides, r = Ea.parent && Ea.parent.provides;
		r === n && (n = Ea.provides = Object.create(r)), n[e] = t;
	}
}
function er(e, t, n = !1) {
	let r = Da();
	if (r || si) {
		let i = si ? si._context.provides : r ? r.parent == null || r.ce ? r.vnode.appContext && r.vnode.appContext.provides : r.parent.provides : void 0;
		if (i && e in i) return i[e];
		if (arguments.length > 1) return n && N(t) ? t.call(r && r.proxy) : t;
	}
}
var tr = /* @__PURE__ */ Symbol.for("v-scx"), nr = () => er(tr);
function rr(e, t) {
	return ir(e, null, t);
}
function G(e, t, n) {
	return ir(e, t, n);
}
function ir(e, t, n = E) {
	let { immediate: r, deep: i, flush: a, once: o } = n, s = A({}, n), c = t && r || !t && a !== "post", l;
	if (Na) {
		if (a === "sync") {
			let e = nr();
			l = e.__watcherHandles ||= [];
		} else if (!c) {
			let e = () => {};
			return e.stop = D, e.resume = D, e.pause = D, e;
		}
	}
	let u = Ea;
	s.call = (e, t, n) => kn(e, u, t, n);
	let d = !1;
	a === "post" ? s.scheduler = (e) => {
		Ri(e, u && u.suspense);
	} : a !== "sync" && (d = !0, s.scheduler = (e, t) => {
		t ? e() : Vn(e);
	}), s.augmentJob = (e) => {
		t && (e.flags |= 4), d && (e.flags |= 2, u && (e.id = u.uid, e.i = u));
	};
	let f = En(e, t, s);
	return Na && (l ? l.push(f) : c && f()), f;
}
function ar(e, t, n) {
	let r = this.proxy, i = P(e) ? e.includes(".") ? or(r, e) : () => r[e] : e.bind(r, r), a;
	N(t) ? a = t : (a = t.handler, n = t);
	let o = Aa(this), s = ir(i, a.bind(r), n);
	return o(), s;
}
function or(e, t) {
	let n = t.split(".");
	return () => {
		let t = e;
		for (let e = 0; e < n.length && t; e++) t = t[n[e]];
		return t;
	};
}
var sr = /* @__PURE__ */ Symbol("_vte"), cr = (e) => e.__isTeleport, lr = /* @__PURE__ */ Symbol("_leaveCb");
function ur(e, t) {
	e.shapeFlag & 6 && e.component ? (e.transition = t, ur(e.component.subTree, t)) : e.shapeFlag & 128 ? (e.ssContent.transition = t.clone(e.ssContent), e.ssFallback.transition = t.clone(e.ssFallback)) : e.transition = t;
}
// @__NO_SIDE_EFFECTS__
function dr(e, t) {
	return N(e) ? /* @__PURE__ */ A({ name: e.name }, t, { setup: e }) : e;
}
function fr(e) {
	e.ids = [
		e.ids[0] + e.ids[2]++ + "-",
		0,
		0
	];
}
function pr(e) {
	let t = Da(), n = /* @__PURE__ */ H(null);
	if (t) {
		let r = t.refs === E ? t.refs = {} : t.refs;
		Object.defineProperty(r, e, {
			enumerable: !0,
			get: () => n.value,
			set: (e) => n.value = e
		});
	}
	return n;
}
function mr(e, t) {
	let n;
	return !!((n = Object.getOwnPropertyDescriptor(e, t)) && !n.configurable);
}
var hr = /* @__PURE__ */ new WeakMap();
function gr(e, t, n, r, i = !1) {
	if (M(e)) {
		e.forEach((e, a) => gr(e, t && (M(t) ? t[a] : t), n, r, i));
		return;
	}
	if (vr(r) && !i) {
		r.shapeFlag & 512 && r.type.__asyncResolved && r.component.subTree.component && gr(e, t, n, r.component.subTree);
		return;
	}
	let a = r.shapeFlag & 4 ? Ha(r.component) : r.el, o = i ? null : a, { i: s, r: c } = e, l = t && t.r, u = s.refs === E ? s.refs = {} : s.refs, d = s.setupState, f = /* @__PURE__ */ B(d), p = d === E ? ne : (e) => !mr(u, e) && j(f, e), m = (e, t) => !(t && mr(u, t));
	if (l != null && l !== c) {
		if (_r(t), P(l)) u[l] = null, p(l) && (d[l] = null);
		else if (/* @__PURE__ */ hn(l)) {
			let e = t;
			m(l, e.k) && (l.value = null), e.k && (u[e.k] = null);
		}
	}
	if (N(c)) On(c, s, 12, [o, u]);
	else {
		let t = P(c), r = /* @__PURE__ */ hn(c);
		if (t || r) {
			let s = () => {
				if (e.f) {
					let n = t ? p(c) ? d[c] : u[c] : m(c) || !e.k ? c.value : u[e.k];
					if (i) M(n) && re(n, a);
					else if (M(n)) n.includes(a) || n.push(a);
					else if (t) u[c] = [a], p(c) && (d[c] = u[c]);
					else {
						let t = [a];
						m(c, e.k) && (c.value = t), e.k && (u[e.k] = t);
					}
				} else t ? (u[c] = o, p(c) && (d[c] = o)) : r && (m(c, e.k) && (c.value = o), e.k && (u[e.k] = o));
			};
			if (o) {
				let t = () => {
					s(), hr.delete(e);
				};
				t.id = -1, hr.set(e, t), Ri(t, n);
			} else _r(e), s();
		}
	}
}
function _r(e) {
	let t = hr.get(e);
	t && (t.flags |= 8, hr.delete(e));
}
Ee().requestIdleCallback, Ee().cancelIdleCallback;
var vr = (e) => !!e.type.__asyncLoader, yr = (e) => e.type.__isKeepAlive;
function br(e, t) {
	Sr(e, "a", t);
}
function xr(e, t) {
	Sr(e, "da", t);
}
function Sr(e, t, n = Ea) {
	let r = e.__wdc ||= () => {
		let t = n;
		for (; t;) {
			if (t.isDeactivated) return;
			t = t.parent;
		}
		return e();
	};
	if (wr(t, r, n), n) {
		let e = n.parent;
		for (; e && e.parent;) yr(e.parent.vnode) && Cr(r, t, n, e), e = e.parent;
	}
}
function Cr(e, t, n, r) {
	let i = wr(t, e, r, !0);
	jr(() => {
		re(r[t], i);
	}, n);
}
function wr(e, t, n = Ea, r = !1) {
	if (n) {
		let i = n[e] || (n[e] = []), a = t.__weh ||= (...r) => {
			ct();
			let i = Aa(n), a = kn(t, n, e, r);
			return i(), lt(), a;
		};
		return r ? i.unshift(a) : i.push(a), a;
	}
}
var Tr = (e) => (t, n = Ea) => {
	(!Na || e === "sp") && wr(e, (...e) => t(...e), n);
}, Er = Tr("bm"), Dr = Tr("m"), Or = Tr("bu"), kr = Tr("u"), Ar = Tr("bum"), jr = Tr("um"), Mr = Tr("sp"), Nr = Tr("rtg"), Pr = Tr("rtc");
function Fr(e, t = Ea) {
	wr("ec", e, t);
}
var Ir = /* @__PURE__ */ Symbol.for("v-ndc");
function Lr(e, t, n, r) {
	let i, a = n && n[r], o = M(e);
	if (o || P(e)) {
		let n = o && /* @__PURE__ */ cn(e), r = !1, s = !1;
		n && (r = !/* @__PURE__ */ un(e), s = /* @__PURE__ */ ln(e), e = St(e)), i = Array(e.length);
		for (let n = 0, o = e.length; n < o; n++) i[n] = t(r ? s ? mn(pn(e[n])) : pn(e[n]) : e[n], n, void 0, a && a[n]);
	} else if (typeof e == "number") {
		i = Array(e);
		for (let n = 0; n < e; n++) i[n] = t(n + 1, n, void 0, a && a[n]);
	} else if (F(e)) if (e[Symbol.iterator]) i = Array.from(e, (e, n) => t(e, n, void 0, a && a[n]));
	else {
		let n = Object.keys(e);
		i = Array(n.length);
		for (let r = 0, o = n.length; r < o; r++) {
			let o = n[r];
			i[r] = t(e[o], o, r, a && a[r]);
		}
	}
	else i = [];
	return n && (n[r] = i), i;
}
var Rr = (e) => e ? Ma(e) ? Ha(e) : Rr(e.parent) : null, zr = /* @__PURE__ */ A(/* @__PURE__ */ Object.create(null), {
	$: (e) => e,
	$el: (e) => e.vnode.el,
	$data: (e) => e.data,
	$props: (e) => e.props,
	$attrs: (e) => e.attrs,
	$slots: (e) => e.slots,
	$refs: (e) => e.refs,
	$parent: (e) => Rr(e.parent),
	$root: (e) => Rr(e.root),
	$host: (e) => e.ce,
	$emit: (e) => e.emit,
	$options: (e) => Jr(e),
	$forceUpdate: (e) => e.f ||= () => {
		Vn(e.update);
	},
	$nextTick: (e) => e.n ||= zn.bind(e.proxy),
	$watch: (e) => ar.bind(e)
}), Br = (e, t) => e !== E && !e.__isScriptSetup && j(e, t), Vr = {
	get({ _: e }, t) {
		if (t === "__v_skip") return !0;
		let { ctx: n, setupState: r, data: i, props: a, accessCache: o, type: s, appContext: c } = e;
		if (t[0] !== "$") {
			let e = o[t];
			if (e !== void 0) switch (e) {
				case 1: return r[t];
				case 2: return i[t];
				case 4: return n[t];
				case 3: return a[t];
			}
			else if (Br(r, t)) return o[t] = 1, r[t];
			else if (i !== E && j(i, t)) return o[t] = 2, i[t];
			else if (j(a, t)) return o[t] = 3, a[t];
			else if (n !== E && j(n, t)) return o[t] = 4, n[t];
			else Ur && (o[t] = 0);
		}
		let l = zr[t], u, d;
		if (l) return t === "$attrs" && yt(e.attrs, "get", ""), l(e);
		if ((u = s.__cssModules) && (u = u[t])) return u;
		if (n !== E && j(n, t)) return o[t] = 4, n[t];
		if (d = c.config.globalProperties, j(d, t)) return d[t];
	},
	set({ _: e }, t, n) {
		let { data: r, setupState: i, ctx: a } = e;
		return Br(i, t) ? (i[t] = n, !0) : r !== E && j(r, t) ? (r[t] = n, !0) : j(e.props, t) || t[0] === "$" && t.slice(1) in e ? !1 : (a[t] = n, !0);
	},
	has({ _: { data: e, setupState: t, accessCache: n, ctx: r, appContext: i, props: a, type: o } }, s) {
		let c;
		return !!(n[s] || e !== E && s[0] !== "$" && j(e, s) || Br(t, s) || j(a, s) || j(r, s) || j(zr, s) || j(i.config.globalProperties, s) || (c = o.__cssModules) && c[s]);
	},
	defineProperty(e, t, n) {
		return n.get == null ? j(n, "value") && this.set(e, t, n.value, null) : e._.accessCache[t] = 0, Reflect.defineProperty(e, t, n);
	}
};
function Hr(e) {
	return M(e) ? e.reduce((e, t) => (e[t] = null, e), {}) : e;
}
var Ur = !0;
function Wr(e) {
	let t = Jr(e), n = e.proxy, r = e.ctx;
	Ur = !1, t.beforeCreate && Kr(t.beforeCreate, e, "bc");
	let { data: i, computed: a, methods: o, watch: s, provide: c, inject: l, created: u, beforeMount: d, mounted: f, beforeUpdate: p, updated: m, activated: h, deactivated: g, beforeDestroy: _, beforeUnmount: v, destroyed: y, unmounted: b, render: x, renderTracked: S, renderTriggered: ee, errorCaptured: C, serverPrefetch: w, expose: T, inheritAttrs: E, components: te, directives: ne, filters: O } = t;
	if (l && Gr(l, r, null), o) for (let e in o) {
		let t = o[e];
		N(t) && (r[e] = t.bind(n));
	}
	if (i) {
		let t = i.call(n, n);
		F(t) && (e.data = /* @__PURE__ */ nn(t));
	}
	if (Ur = !0, a) for (let e in a) {
		let t = a[e], i = Y({
			get: N(t) ? t.bind(n, n) : N(t.get) ? t.get.bind(n, n) : D,
			set: !N(t) && N(t.set) ? t.set.bind(n) : D
		});
		Object.defineProperty(r, e, {
			enumerable: !0,
			configurable: !0,
			get: () => i.value,
			set: (e) => i.value = e
		});
	}
	if (s) for (let e in s) qr(s[e], r, n, e);
	if (c) {
		let e = N(c) ? c.call(n) : c;
		Reflect.ownKeys(e).forEach((t) => {
			$n(t, e[t]);
		});
	}
	u && Kr(u, e, "c");
	function k(e, t) {
		M(t) ? t.forEach((t) => e(t.bind(n))) : t && e(t.bind(n));
	}
	if (k(Er, d), k(Dr, f), k(Or, p), k(kr, m), k(br, h), k(xr, g), k(Fr, C), k(Pr, S), k(Nr, ee), k(Ar, v), k(jr, b), k(Mr, w), M(T)) if (T.length) {
		let t = e.exposed ||= {};
		T.forEach((e) => {
			Object.defineProperty(t, e, {
				get: () => n[e],
				set: (t) => n[e] = t,
				enumerable: !0
			});
		});
	} else e.exposed ||= {};
	x && e.render === D && (e.render = x), E != null && (e.inheritAttrs = E), te && (e.components = te), ne && (e.directives = ne), w && fr(e);
}
function Gr(e, t, n = D) {
	M(e) && (e = $r(e));
	for (let n in e) {
		let r = e[n], i;
		i = F(r) ? "default" in r ? er(r.from || n, r.default, !0) : er(r.from || n) : er(r), /* @__PURE__ */ hn(i) ? Object.defineProperty(t, n, {
			enumerable: !0,
			configurable: !0,
			get: () => i.value,
			set: (e) => i.value = e
		}) : t[n] = i;
	}
}
function Kr(e, t, n) {
	kn(M(e) ? e.map((e) => e.bind(t.proxy)) : e.bind(t.proxy), t, n);
}
function qr(e, t, n, r) {
	let i = r.includes(".") ? or(n, r) : () => n[r];
	if (P(e)) {
		let n = t[e];
		N(n) && G(i, n);
	} else if (N(e)) G(i, e.bind(n));
	else if (F(e)) if (M(e)) e.forEach((e) => qr(e, t, n, r));
	else {
		let r = N(e.handler) ? e.handler.bind(n) : t[e.handler];
		N(r) && G(i, r, e);
	}
}
function Jr(e) {
	let t = e.type, { mixins: n, extends: r } = t, { mixins: i, optionsCache: a, config: { optionMergeStrategies: o } } = e.appContext, s = a.get(t), c;
	return s ? c = s : !i.length && !n && !r ? c = t : (c = {}, i.length && i.forEach((e) => Yr(c, e, o, !0)), Yr(c, t, o)), F(t) && a.set(t, c), c;
}
function Yr(e, t, n, r = !1) {
	let { mixins: i, extends: a } = t;
	a && Yr(e, a, n, !0), i && i.forEach((t) => Yr(e, t, n, !0));
	for (let i in t) if (!(r && i === "expose")) {
		let r = Xr[i] || n && n[i];
		e[i] = r ? r(e[i], t[i]) : t[i];
	}
	return e;
}
var Xr = {
	data: Zr,
	props: ni,
	emits: ni,
	methods: ti,
	computed: ti,
	beforeCreate: ei,
	created: ei,
	beforeMount: ei,
	mounted: ei,
	beforeUpdate: ei,
	updated: ei,
	beforeDestroy: ei,
	beforeUnmount: ei,
	destroyed: ei,
	unmounted: ei,
	activated: ei,
	deactivated: ei,
	errorCaptured: ei,
	serverPrefetch: ei,
	components: ti,
	directives: ti,
	watch: ri,
	provide: Zr,
	inject: Qr
};
function Zr(e, t) {
	return t ? e ? function() {
		return A(N(e) ? e.call(this, this) : e, N(t) ? t.call(this, this) : t);
	} : t : e;
}
function Qr(e, t) {
	return ti($r(e), $r(t));
}
function $r(e) {
	if (M(e)) {
		let t = {};
		for (let n = 0; n < e.length; n++) t[e[n]] = e[n];
		return t;
	}
	return e;
}
function ei(e, t) {
	return e ? [...new Set([].concat(e, t))] : t;
}
function ti(e, t) {
	return e ? A(/* @__PURE__ */ Object.create(null), e, t) : t;
}
function ni(e, t) {
	return e ? M(e) && M(t) ? [.../* @__PURE__ */ new Set([...e, ...t])] : A(/* @__PURE__ */ Object.create(null), Hr(e), Hr(t ?? {})) : t;
}
function ri(e, t) {
	if (!e) return t;
	if (!t) return e;
	let n = A(/* @__PURE__ */ Object.create(null), e);
	for (let r in t) n[r] = ei(e[r], t[r]);
	return n;
}
function ii() {
	return {
		app: null,
		config: {
			isNativeTag: ne,
			performance: !1,
			globalProperties: {},
			optionMergeStrategies: {},
			errorHandler: void 0,
			warnHandler: void 0,
			compilerOptions: {}
		},
		mixins: [],
		components: {},
		directives: {},
		provides: /* @__PURE__ */ Object.create(null),
		optionsCache: /* @__PURE__ */ new WeakMap(),
		propsCache: /* @__PURE__ */ new WeakMap(),
		emitsCache: /* @__PURE__ */ new WeakMap()
	};
}
var ai = 0;
function oi(e, t) {
	return function(n, r = null) {
		N(n) || (n = A({}, n)), r != null && !F(r) && (r = null);
		let i = ii(), a = /* @__PURE__ */ new WeakSet(), o = [], s = !1, c = i.app = {
			_uid: ai++,
			_component: n,
			_props: r,
			_container: null,
			_context: i,
			_instance: null,
			version: Wa,
			get config() {
				return i.config;
			},
			set config(e) {},
			use(e, ...t) {
				return a.has(e) || (e && N(e.install) ? (a.add(e), e.install(c, ...t)) : N(e) && (a.add(e), e(c, ...t))), c;
			},
			mixin(e) {
				return i.mixins.includes(e) || i.mixins.push(e), c;
			},
			component(e, t) {
				return t ? (i.components[e] = t, c) : i.components[e];
			},
			directive(e, t) {
				return t ? (i.directives[e] = t, c) : i.directives[e];
			},
			mount(a, o, l) {
				if (!s) {
					let u = c._ceVNode || fa(n, r);
					return u.appContext = i, l === !0 ? l = "svg" : l === !1 && (l = void 0), o && t ? t(u, a) : e(u, a, l), s = !0, c._container = a, a.__vue_app__ = c, Ha(u.component);
				}
			},
			onUnmount(e) {
				o.push(e);
			},
			unmount() {
				s && (kn(o, c._instance, 16), e(null, c._container), delete c._container.__vue_app__);
			},
			provide(e, t) {
				return i.provides[e] = t, c;
			},
			runWithContext(e) {
				let t = si;
				si = c;
				try {
					return e();
				} finally {
					si = t;
				}
			}
		};
		return c;
	};
}
var si = null, ci = (e, t) => t === "modelValue" || t === "model-value" ? e.modelModifiers : e[`${t}Modifiers`] || e[`${L(t)}Modifiers`] || e[`${ve(t)}Modifiers`];
function li(e, t, ...n) {
	if (e.isUnmounted) return;
	let r = e.vnode.props || E, i = n, a = t.startsWith("update:"), o = a && ci(r, t.slice(7));
	o && (o.trim && (i = n.map((e) => P(e) ? e.trim() : e)), o.number && (i = n.map(we)));
	let s, c = r[s = be(t)] || r[s = be(L(t))];
	!c && a && (c = r[s = be(ve(t))]), c && kn(c, e, 6, i);
	let l = r[s + "Once"];
	if (l) {
		if (!e.emitted) e.emitted = {};
		else if (e.emitted[s]) return;
		e.emitted[s] = !0, kn(l, e, 6, i);
	}
}
var ui = /* @__PURE__ */ new WeakMap();
function di(e, t, n = !1) {
	let r = n ? ui : t.emitsCache, i = r.get(e);
	if (i !== void 0) return i;
	let a = e.emits, o = {}, s = !1;
	if (!N(e)) {
		let r = (e) => {
			let n = di(e, t, !0);
			n && (s = !0, A(o, n));
		};
		!n && t.mixins.length && t.mixins.forEach(r), e.extends && r(e.extends), e.mixins && e.mixins.forEach(r);
	}
	return !a && !s ? (F(e) && r.set(e, null), null) : (M(a) ? a.forEach((e) => o[e] = null) : A(o, a), F(e) && r.set(e, o), o);
}
function fi(e, t) {
	return !e || !O(t) ? !1 : (t = t.slice(2), t = t === "Once" ? t : t.replace(/Once$/, ""), j(e, t[0].toLowerCase() + t.slice(1)) || j(e, ve(t)) || j(e, t));
}
function pi(e) {
	let { type: t, vnode: n, proxy: r, withProxy: i, propsOptions: [a], slots: o, attrs: s, emit: c, render: l, renderCache: u, props: d, data: f, setupState: p, ctx: m, inheritAttrs: h } = e, g = Xn(e), _, v;
	try {
		if (n.shapeFlag & 4) {
			let e = i || r, t = e;
			_ = va(l.call(t, e, u, d, p, f, m)), v = s;
		} else {
			let e = t;
			_ = va(e.length > 1 ? e(d, {
				attrs: s,
				slots: o,
				emit: c
			}) : e(d, null)), v = t.props ? s : mi(s);
		}
	} catch (t) {
		ta.length = 0, An(t, e, 1), _ = fa($i);
	}
	let y = _;
	if (v && h !== !1) {
		let e = Object.keys(v), { shapeFlag: t } = y;
		e.length && t & 7 && (a && e.some(k) && (v = hi(v, a)), y = ha(y, v, !1, !0));
	}
	return n.dirs && (y = ha(y, null, !1, !0), y.dirs = y.dirs ? y.dirs.concat(n.dirs) : n.dirs), n.transition && ur(y, n.transition), _ = y, Xn(g), _;
}
var mi = (e) => {
	let t;
	for (let n in e) (n === "class" || n === "style" || O(n)) && ((t ||= {})[n] = e[n]);
	return t;
}, hi = (e, t) => {
	let n = {};
	for (let r in e) (!k(r) || !(r.slice(9) in t)) && (n[r] = e[r]);
	return n;
};
function gi(e, t, n) {
	let { props: r, children: i, component: a } = e, { props: o, children: s, patchFlag: c } = t, l = a.emitsOptions;
	if (t.dirs || t.transition) return !0;
	if (n && c >= 0) {
		if (c & 1024) return !0;
		if (c & 16) return r ? _i(r, o, l) : !!o;
		if (c & 8) {
			let e = t.dynamicProps;
			for (let t = 0; t < e.length; t++) {
				let n = e[t];
				if (vi(o, r, n) && !fi(l, n)) return !0;
			}
		}
	} else return (i || s) && (!s || !s.$stable) ? !0 : r === o ? !1 : r ? !o || _i(r, o, l) : !!o;
	return !1;
}
function _i(e, t, n) {
	let r = Object.keys(t);
	if (r.length !== Object.keys(e).length) return !0;
	for (let i = 0; i < r.length; i++) {
		let a = r[i];
		if (vi(t, e, a) && !fi(n, a)) return !0;
	}
	return !1;
}
function vi(e, t, n) {
	let r = e[n], i = t[n];
	return n === "style" && F(r) && F(i) ? !Le(r, i) : r !== i;
}
function yi({ vnode: e, parent: t, suspense: n }, r) {
	for (; t;) {
		let n = t.subTree;
		if (n.suspense && n.suspense.activeBranch === e && (n.suspense.vnode.el = n.el = r, e = n), n === e) (e = t.vnode).el = r, t = t.parent;
		else break;
	}
	n && n.activeBranch === e && (n.vnode.el = r);
}
var bi = {}, xi = () => Object.create(bi), Si = (e) => Object.getPrototypeOf(e) === bi;
function Ci(e, t, n, r = !1) {
	let i = {}, a = xi();
	e.propsDefaults = /* @__PURE__ */ Object.create(null), Ti(e, t, i, a);
	for (let t in e.propsOptions[0]) t in i || (i[t] = void 0);
	e.props = n ? r ? i : /* @__PURE__ */ rn(i) : e.type.props ? i : a, e.attrs = a;
}
function wi(e, t, n, r) {
	let { props: i, attrs: a, vnode: { patchFlag: o } } = e, s = /* @__PURE__ */ B(i), [c] = e.propsOptions, l = !1;
	if ((r || o > 0) && !(o & 16)) {
		if (o & 8) {
			let n = e.vnode.dynamicProps;
			for (let r = 0; r < n.length; r++) {
				let o = n[r];
				if (fi(e.emitsOptions, o)) continue;
				let u = t[o];
				if (c) if (j(a, o)) u !== a[o] && (a[o] = u, l = !0);
				else {
					let t = L(o);
					i[t] = Ei(c, s, t, u, e, !1);
				}
				else u !== a[o] && (a[o] = u, l = !0);
			}
		}
	} else {
		Ti(e, t, i, a) && (l = !0);
		let r;
		for (let a in s) (!t || !j(t, a) && ((r = ve(a)) === a || !j(t, r))) && (c ? n && (n[a] !== void 0 || n[r] !== void 0) && (i[a] = Ei(c, s, a, void 0, e, !0)) : delete i[a]);
		if (a !== s) for (let e in a) (!t || !j(t, e)) && (delete a[e], l = !0);
	}
	l && bt(e.attrs, "set", "");
}
function Ti(e, t, n, r) {
	let [i, a] = e.propsOptions, o = !1, s;
	if (t) for (let c in t) {
		if (me(c)) continue;
		let l = t[c], u;
		i && j(i, u = L(c)) ? !a || !a.includes(u) ? n[u] = l : (s ||= {})[u] = l : fi(e.emitsOptions, c) || (!(c in r) || l !== r[c]) && (r[c] = l, o = !0);
	}
	if (a) {
		let t = /* @__PURE__ */ B(n), r = s || E;
		for (let o = 0; o < a.length; o++) {
			let s = a[o];
			n[s] = Ei(i, t, s, r[s], e, !j(r, s));
		}
	}
	return o;
}
function Ei(e, t, n, r, i, a) {
	let o = e[n];
	if (o != null) {
		let e = j(o, "default");
		if (e && r === void 0) {
			let e = o.default;
			if (o.type !== Function && !o.skipFactory && N(e)) {
				let { propsDefaults: a } = i;
				if (n in a) r = a[n];
				else {
					let o = Aa(i);
					r = a[n] = e.call(null, t), o();
				}
			} else r = e;
			i.ce && i.ce._setProp(n, r);
		}
		o[0] && (a && !e ? r = !1 : o[1] && (r === "" || r === ve(n)) && (r = !0));
	}
	return r;
}
var Di = /* @__PURE__ */ new WeakMap();
function Oi(e, t, n = !1) {
	let r = n ? Di : t.propsCache, i = r.get(e);
	if (i) return i;
	let a = e.props, o = {}, s = [], c = !1;
	if (!N(e)) {
		let r = (e) => {
			c = !0;
			let [n, r] = Oi(e, t, !0);
			A(o, n), r && s.push(...r);
		};
		!n && t.mixins.length && t.mixins.forEach(r), e.extends && r(e.extends), e.mixins && e.mixins.forEach(r);
	}
	if (!a && !c) return F(e) && r.set(e, te), te;
	if (M(a)) for (let e = 0; e < a.length; e++) {
		let t = L(a[e]);
		ki(t) && (o[t] = E);
	}
	else if (a) for (let e in a) {
		let t = L(e);
		if (ki(t)) {
			let n = a[e], r = o[t] = M(n) || N(n) ? { type: n } : A({}, n), i = r.type, c = !1, l = !0;
			if (M(i)) for (let e = 0; e < i.length; ++e) {
				let t = i[e], n = N(t) && t.name;
				if (n === "Boolean") {
					c = !0;
					break;
				}
				n === "String" && (l = !1);
			}
			else c = N(i) && i.name === "Boolean";
			r[0] = c, r[1] = l, (c || j(r, "default")) && s.push(t);
		}
	}
	let l = [o, s];
	return F(e) && r.set(e, l), l;
}
function ki(e) {
	return e[0] !== "$" && !me(e);
}
var Ai = (e) => e === "_" || e === "_ctx" || e === "$stable", ji = (e) => M(e) ? e.map(va) : [va(e)], Mi = (e, t, n) => {
	if (t._n) return t;
	let r = Zn((...e) => ji(t(...e)), n);
	return r._c = !1, r;
}, Ni = (e, t, n) => {
	let r = e._ctx;
	for (let n in e) {
		if (Ai(n)) continue;
		let i = e[n];
		if (N(i)) t[n] = Mi(n, i, r);
		else if (i != null) {
			let e = ji(i);
			t[n] = () => e;
		}
	}
}, Pi = (e, t) => {
	let n = ji(t);
	e.slots.default = () => n;
}, Fi = (e, t, n) => {
	for (let r in t) (n || !Ai(r)) && (e[r] = t[r]);
}, Ii = (e, t, n) => {
	let r = e.slots = xi();
	if (e.vnode.shapeFlag & 32) {
		let e = t._;
		e ? (Fi(r, t, n), n && Ce(r, "_", e, !0)) : Ni(t, r);
	} else t && Pi(e, t);
}, Li = (e, t, n) => {
	let { vnode: r, slots: i } = e, a = !0, o = E;
	if (r.shapeFlag & 32) {
		let e = t._;
		e ? n && e === 1 ? a = !1 : Fi(i, t, n) : (a = !t.$stable, Ni(t, i)), o = t;
	} else t && (Pi(e, t), o = { default: 1 });
	if (a) for (let e in i) !Ai(e) && o[e] == null && delete i[e];
}, Ri = Xi;
function zi(e) {
	return Bi(e);
}
function Bi(e, t) {
	let n = Ee();
	n.__VUE__ = !0;
	let { insert: r, remove: i, patchProp: a, createElement: o, createText: s, createComment: c, setText: l, setElementText: u, parentNode: d, nextSibling: f, setScopeId: p = D, insertStaticContent: m } = e, h = (e, t, n, r = null, i = null, a = null, o = void 0, s = null, c = !!t.dynamicChildren) => {
		if (e === t) return;
		e && !la(e, t) && (r = ue(e), N(e, i, a, !0), e = null), t.patchFlag === -2 && (c = !1, t.dynamicChildren = null);
		let { type: l, ref: u, shapeFlag: d } = t;
		switch (l) {
			case Qi:
				g(e, t, n, r);
				break;
			case $i:
				_(e, t, n, r);
				break;
			case ea:
				e ?? v(t, n, r, o);
				break;
			case Zi:
				O(e, t, n, r, i, a, o, s, c);
				break;
			default: d & 1 ? x(e, t, n, r, i, a, o, s, c) : d & 6 ? k(e, t, n, r, i, a, o, s, c) : (d & 64 || d & 128) && l.process(e, t, n, r, i, a, o, s, c, pe);
		}
		u != null && i ? gr(u, e && e.ref, a, t || e, !t) : u == null && e && e.ref != null && gr(e.ref, null, a, e, !0);
	}, g = (e, t, n, i) => {
		if (e == null) r(t.el = s(t.children), n, i);
		else {
			let n = t.el = e.el;
			t.children !== e.children && l(n, t.children);
		}
	}, _ = (e, t, n, i) => {
		e == null ? r(t.el = c(t.children || ""), n, i) : t.el = e.el;
	}, v = (e, t, n, r) => {
		[e.el, e.anchor] = m(e.children, t, n, r, e.el, e.anchor);
	}, y = ({ el: e, anchor: t }, n, i) => {
		let a;
		for (; e && e !== t;) a = f(e), r(e, n, i), e = a;
		r(t, n, i);
	}, b = ({ el: e, anchor: t }) => {
		let n;
		for (; e && e !== t;) n = f(e), i(e), e = n;
		i(t);
	}, x = (e, t, n, r, i, a, o, s, c) => {
		if (t.type === "svg" ? o = "svg" : t.type === "math" && (o = "mathml"), e == null) S(t, n, r, i, a, o, s, c);
		else {
			let n = e.el && e.el._isVueCE ? e.el : null;
			try {
				n && n._beginPatch(), w(e, t, i, a, o, s, c);
			} finally {
				n && n._endPatch();
			}
		}
	}, S = (e, t, n, i, s, c, l, d) => {
		let f, p, { props: m, shapeFlag: h, transition: g, dirs: _ } = e;
		if (f = e.el = o(e.type, c, m && m.is, m), h & 8 ? u(f, e.children) : h & 16 && C(e.children, f, null, i, s, Vi(e, c), l, d), _ && Qn(e, null, i, "created"), ee(f, e, e.scopeId, l, i), m) {
			for (let e in m) e !== "value" && !me(e) && a(f, e, null, m[e], c, i);
			"value" in m && a(f, "value", null, m.value, c), (p = m.onVnodeBeforeMount) && Sa(p, i, e);
		}
		_ && Qn(e, null, i, "beforeMount");
		let v = Ui(s, g);
		v && g.beforeEnter(f), r(f, t, n), ((p = m && m.onVnodeMounted) || v || _) && Ri(() => {
			try {
				p && Sa(p, i, e), v && g.enter(f), _ && Qn(e, null, i, "mounted");
			} finally {}
		}, s);
	}, ee = (e, t, n, r, i) => {
		if (n && p(e, n), r) for (let t = 0; t < r.length; t++) p(e, r[t]);
		if (i) {
			let n = i.subTree;
			if (t === n || Yi(n.type) && (n.ssContent === t || n.ssFallback === t)) {
				let t = i.vnode;
				ee(e, t, t.scopeId, t.slotScopeIds, i.parent);
			}
		}
	}, C = (e, t, n, r, i, a, o, s, c = 0) => {
		for (let l = c; l < e.length; l++) {
			let c = e[l] = s ? ya(e[l]) : va(e[l]);
			h(null, c, t, n, r, i, a, o, s);
		}
	}, w = (e, t, n, r, i, o, s) => {
		let c = t.el = e.el, { patchFlag: l, dynamicChildren: d, dirs: f } = t;
		l |= e.patchFlag & 16;
		let p = e.props || E, m = t.props || E, h;
		if (n && Hi(n, !1), (h = m.onVnodeBeforeUpdate) && Sa(h, n, t, e), f && Qn(t, e, n, "beforeUpdate"), n && Hi(n, !0), d && (!e.dynamicChildren || e.dynamicChildren.length !== d.length) && (l = 0, s = !1, d = null), (p.innerHTML && m.innerHTML == null || p.textContent && m.textContent == null) && u(c, ""), d ? T(e.dynamicChildren, d, c, n, r, Vi(t, i), o) : s || M(e, t, c, null, n, r, Vi(t, i), o, !1), l > 0) {
			if (l & 16) ne(c, p, m, n, i);
			else if (l & 2 && p.class !== m.class && a(c, "class", null, m.class, i), l & 4 && a(c, "style", p.style, m.style, i), l & 8) {
				let e = t.dynamicProps;
				for (let t = 0; t < e.length; t++) {
					let r = e[t], o = p[r], s = m[r];
					(s !== o || r === "value") && a(c, r, o, s, i, n);
				}
			}
			l & 1 && e.children !== t.children && u(c, t.children);
		} else !s && d == null && ne(c, p, m, n, i);
		((h = m.onVnodeUpdated) || f) && Ri(() => {
			h && Sa(h, n, t, e), f && Qn(t, e, n, "updated");
		}, r);
	}, T = (e, t, n, r, i, a, o) => {
		for (let s = 0; s < t.length; s++) {
			let c = e[s], l = t[s], u = c.el && (c.type === Zi || !la(c, l) || c.shapeFlag & 198) ? d(c.el) : n;
			h(c, l, u, null, r, i, a, o, !0);
		}
	}, ne = (e, t, n, r, i) => {
		if (t !== n) {
			if (t !== E) for (let o in t) !me(o) && !(o in n) && a(e, o, t[o], null, i, r);
			for (let o in n) {
				if (me(o)) continue;
				let s = n[o], c = t[o];
				s !== c && o !== "value" && a(e, o, c, s, i, r);
			}
			"value" in n && a(e, "value", t.value, n.value, i);
		}
	}, O = (e, t, n, i, a, o, c, l, u) => {
		let d = t.el = e ? e.el : s(""), f = t.anchor = e ? e.anchor : s(""), { patchFlag: p, dynamicChildren: m, slotScopeIds: h } = t;
		h && (l = l ? l.concat(h) : h), e == null ? (r(d, n, i), r(f, n, i), C(t.children || [], n, f, a, o, c, l, u)) : p > 0 && p & 64 && m && e.dynamicChildren && e.dynamicChildren.length === m.length ? (T(e.dynamicChildren, m, n, a, o, c, l), (t.key != null || a && t === a.subTree) && Wi(e, t, !0)) : M(e, t, n, f, a, o, c, l, u);
	}, k = (e, t, n, r, i, a, o, s, c) => {
		t.slotScopeIds = s, e == null ? t.shapeFlag & 512 ? i.ctx.activate(t, n, r, o, c) : A(t, n, r, i, a, o, c) : re(e, t, c);
	}, A = (e, t, n, r, i, a, o) => {
		let s = e.component = Ta(e, r, i);
		if (yr(e) && (s.ctx.renderer = pe), Pa(s, !1, o), s.asyncDep) {
			if (i && i.registerDep(s, ie, o), !e.el) {
				let r = s.subTree = fa($i);
				_(null, r, t, n), e.placeholder = r.el;
			}
		} else ie(s, e, t, n, i, a, o);
	}, re = (e, t, n) => {
		let r = t.component = e.component;
		if (gi(e, t, n)) if (r.asyncDep && !r.asyncResolved) {
			j(r, t, n);
			return;
		} else r.next = t, r.update();
		else t.el = e.el, r.vnode = t;
	}, ie = (e, t, n, r, i, a, o) => {
		let s = () => {
			if (e.isMounted) {
				let { next: t, bu: n, u: r, parent: s, vnode: c } = e;
				{
					let n = Ki(e);
					if (n) {
						t && (t.el = c.el, j(e, t, o)), n.asyncDep.then(() => {
							Ri(() => {
								e.isUnmounted || l();
							}, i);
						});
						return;
					}
				}
				let u = t, f;
				Hi(e, !1), t ? (t.el = c.el, j(e, t, o)) : t = c, n && Se(n), (f = t.props && t.props.onVnodeBeforeUpdate) && Sa(f, s, t, c), Hi(e, !0);
				let p = pi(e), m = e.subTree;
				e.subTree = p, h(m, p, d(m.el), ue(m), e, i, a), t.el = p.el, u === null && yi(e, p.el), r && Ri(r, i), (f = t.props && t.props.onVnodeUpdated) && Ri(() => Sa(f, s, t, c), i);
			} else {
				let o, { el: s, props: c } = t, { bm: l, m: u, parent: d, root: f, type: p } = e, m = vr(t);
				if (Hi(e, !1), l && Se(l), !m && (o = c && c.onVnodeBeforeMount) && Sa(o, d, t), Hi(e, !0), s && he) {
					let t = () => {
						e.subTree = pi(e), he(s, e.subTree, e, i, null);
					};
					m && p.__asyncHydrate ? p.__asyncHydrate(s, e, t) : t();
				} else {
					f.ce && f.ce._hasShadowRoot() && f.ce._injectChildStyle(p, e.parent ? e.parent.type : void 0);
					let o = e.subTree = pi(e);
					h(null, o, n, r, e, i, a), t.el = o.el;
				}
				if (u && Ri(u, i), !m && (o = c && c.onVnodeMounted)) {
					let e = t;
					Ri(() => Sa(o, d, e), i);
				}
				(t.shapeFlag & 256 || d && vr(d.vnode) && d.vnode.shapeFlag & 256) && e.a && Ri(e.a, i), e.isMounted = !0, t = n = r = null;
			}
		};
		e.scope.on();
		let c = e.effect = new qe(s);
		e.scope.off();
		let l = e.update = c.run.bind(c), u = e.job = c.runIfDirty.bind(c);
		u.i = e, u.id = e.uid, c.scheduler = () => Vn(u), Hi(e, !0), l();
	}, j = (e, t, n) => {
		t.component = e;
		let r = e.vnode.props;
		e.vnode = t, e.next = null, wi(e, t.props, r, n), Li(e, t.children, n), ct(), Wn(e), lt();
	}, M = (e, t, n, r, i, a, o, s, c = !1) => {
		let l = e && e.children, d = e ? e.shapeFlag : 0, f = t.children, { patchFlag: p, shapeFlag: m } = t;
		if (p > 0) {
			if (p & 128) {
				oe(l, f, n, r, i, a, o, s, c);
				return;
			}
			if (p & 256) {
				ae(l, f, n, r, i, a, o, s, c);
				return;
			}
		}
		m & 8 ? (d & 16 && le(l, i, a), f !== l && u(n, f)) : d & 16 ? m & 16 ? oe(l, f, n, r, i, a, o, s, c) : le(l, i, a, !0) : (d & 8 && u(n, ""), m & 16 && C(f, n, r, i, a, o, s, c));
	}, ae = (e, t, n, r, i, a, o, s, c) => {
		e ||= te, t ||= te;
		let l = e.length, u = t.length, d = Math.min(l, u), f;
		for (f = 0; f < d; f++) {
			let r = t[f] = c ? ya(t[f]) : va(t[f]);
			h(e[f], r, n, null, i, a, o, s, c);
		}
		l > u ? le(e, i, a, !0, !1, d) : C(t, n, r, i, a, o, s, c, d);
	}, oe = (e, t, n, r, i, a, o, s, c) => {
		let l = 0, u = t.length, d = e.length - 1, f = u - 1;
		for (; l <= d && l <= f;) {
			let r = e[l], u = t[l] = c ? ya(t[l]) : va(t[l]);
			if (la(r, u)) h(r, u, n, null, i, a, o, s, c);
			else break;
			l++;
		}
		for (; l <= d && l <= f;) {
			let r = e[d], l = t[f] = c ? ya(t[f]) : va(t[f]);
			if (la(r, l)) h(r, l, n, null, i, a, o, s, c);
			else break;
			d--, f--;
		}
		if (l > d) {
			if (l <= f) {
				let e = f + 1, d = e < u ? t[e].el : r;
				for (; l <= f;) h(null, t[l] = c ? ya(t[l]) : va(t[l]), n, d, i, a, o, s, c), l++;
			}
		} else if (l > f) for (; l <= d;) N(e[l], i, a, !0), l++;
		else {
			let p = l, m = l, g = /* @__PURE__ */ new Map();
			for (l = m; l <= f; l++) {
				let e = t[l] = c ? ya(t[l]) : va(t[l]);
				e.key != null && g.set(e.key, l);
			}
			let _, v = 0, y = f - m + 1, b = !1, x = 0, S = Array(y);
			for (l = 0; l < y; l++) S[l] = 0;
			for (l = p; l <= d; l++) {
				let r = e[l];
				if (v >= y) {
					N(r, i, a, !0);
					continue;
				}
				let u;
				if (r.key != null) u = g.get(r.key);
				else for (_ = m; _ <= f; _++) if (S[_ - m] === 0 && la(r, t[_])) {
					u = _;
					break;
				}
				u === void 0 ? N(r, i, a, !0) : (S[u - m] = l + 1, u >= x ? x = u : b = !0, h(r, t[u], n, null, i, a, o, s, c), v++);
			}
			let ee = b ? Gi(S) : te;
			for (_ = ee.length - 1, l = y - 1; l >= 0; l--) {
				let e = m + l, d = t[e], f = t[e + 1], p = e + 1 < u ? f.el || Ji(f) : r;
				S[l] === 0 ? h(null, d, n, p, i, a, o, s, c) : b && (_ < 0 || l !== ee[_] ? se(d, n, p, 2) : _--);
			}
		}
	}, se = (e, t, n, a, o = null) => {
		let { el: s, type: c, transition: l, children: u, shapeFlag: d } = e;
		if (d & 6) {
			se(e.component.subTree, t, n, a);
			return;
		}
		if (d & 128) {
			e.suspense.move(t, n, a);
			return;
		}
		if (d & 64) {
			c.move(e, t, n, pe);
			return;
		}
		if (c === Zi) {
			r(s, t, n);
			for (let e = 0; e < u.length; e++) se(u[e], t, n, a);
			r(e.anchor, t, n);
			return;
		}
		if (c === ea) {
			y(e, t, n);
			return;
		}
		if (a !== 2 && d & 1 && l) if (a === 0) l.persisted && !s[lr] ? r(s, t, n) : (l.beforeEnter(s), r(s, t, n), Ri(() => l.enter(s), o));
		else {
			let { leave: a, delayLeave: o, afterLeave: c } = l, u = () => {
				e.ctx.isUnmounted ? i(s) : r(s, t, n);
			}, d = () => {
				let e = s._isLeaving || !!s[lr];
				s._isLeaving && s[lr](!0), l.persisted && !e ? u() : a(s, () => {
					u(), c && c();
				});
			};
			o ? o(s, u, d) : d();
		}
		else r(s, t, n);
	}, N = (e, t, n, r = !1, i = !1) => {
		let { type: a, props: o, ref: s, children: c, dynamicChildren: l, shapeFlag: u, patchFlag: d, dirs: f, cacheIndex: p, memo: m } = e;
		if (d === -2 && (i = !1), s != null && (ct(), gr(s, null, n, e, !0), lt()), p != null && (t.renderCache[p] = void 0), u & 256) {
			t.ctx.deactivate(e);
			return;
		}
		let h = u & 1 && f, g = !vr(e), _;
		if (g && (_ = o && o.onVnodeBeforeUnmount) && Sa(_, t, e), u & 6) F(e.component, n, r);
		else {
			if (u & 128) {
				e.suspense.unmount(n, r);
				return;
			}
			h && Qn(e, null, t, "beforeUnmount"), u & 64 ? e.type.remove(e, t, n, pe, r) : l && !l.hasOnce && (a !== Zi || d > 0 && d & 64) ? le(l, t, n, !1, !0) : (a === Zi && d & 384 || !i && u & 16) && le(c, t, n), r && P(e);
		}
		let v = m != null && p == null;
		(g && (_ = o && o.onVnodeUnmounted) || h || v) && Ri(() => {
			_ && Sa(_, t, e), h && Qn(e, null, t, "unmounted"), v && (e.el = null);
		}, n);
	}, P = (e) => {
		let { type: t, el: n, anchor: r, transition: a } = e;
		if (t === Zi) {
			ce(n, r);
			return;
		}
		if (t === ea) {
			b(e);
			return;
		}
		let o = () => {
			i(n), a && !a.persisted && a.afterLeave && a.afterLeave();
		};
		if (e.shapeFlag & 1 && a && !a.persisted) {
			let { leave: t, delayLeave: r } = a, i = () => t(n, o);
			r ? r(e.el, o, i) : i();
		} else o();
	}, ce = (e, t) => {
		let n;
		for (; e !== t;) n = f(e), i(e), e = n;
		i(t);
	}, F = (e, t, n) => {
		let { bum: r, scope: i, job: a, subTree: o, um: s, m: c, a: l } = e;
		qi(c), qi(l), r && Se(r), i.stop(), a && (a.flags |= 8, N(o, e, t, n)), s && Ri(s, t), Ri(() => {
			e.isUnmounted = !0;
		}, t);
	}, le = (e, t, n, r = !1, i = !1, a = 0) => {
		for (let o = a; o < e.length; o++) N(e[o], t, n, r, i);
	}, ue = (e) => {
		if (e.shapeFlag & 6) return ue(e.component.subTree);
		if (e.shapeFlag & 128) return e.suspense.next();
		let t = f(e.anchor || e.el), n = t && t[sr];
		return n ? f(n) : t;
	}, de = !1, fe = (e, t, n) => {
		let r;
		e == null ? t._vnode && (N(t._vnode, null, null, !0), r = t._vnode.component) : h(t._vnode || null, e, t, null, null, null, n), t._vnode = e, de ||= (de = !0, Wn(r), Gn(), !1);
	}, pe = {
		p: h,
		um: N,
		m: se,
		r: P,
		mt: A,
		mc: C,
		pc: M,
		pbc: T,
		n: ue,
		o: e
	}, I, he;
	return t && ([I, he] = t(pe)), {
		render: fe,
		hydrate: I,
		createApp: oi(fe, I)
	};
}
function Vi({ type: e, props: t }, n) {
	return n === "svg" && e === "foreignObject" || n === "mathml" && e === "annotation-xml" && t && t.encoding && t.encoding.includes("html") ? void 0 : n;
}
function Hi({ effect: e, job: t }, n) {
	n ? (e.flags |= 32, t.flags |= 4) : (e.flags &= -33, t.flags &= -5);
}
function Ui(e, t) {
	return (!e || e && !e.pendingBranch) && t && !t.persisted;
}
function Wi(e, t, n = !1) {
	let r = e.children, i = t.children;
	if (M(r) && M(i)) for (let e = 0; e < r.length; e++) {
		let t = r[e], a = i[e];
		a.shapeFlag & 1 && !a.dynamicChildren && ((a.patchFlag <= 0 || a.patchFlag === 32) && (a = i[e] = ya(i[e]), a.el = t.el), !n && a.patchFlag !== -2 && Wi(t, a)), a.type === Qi && (a.patchFlag === -1 && (a = i[e] = ya(a)), a.el = t.el), a.type === $i && !a.el && (a.el = t.el);
	}
}
function Gi(e) {
	let t = e.slice(), n = [0], r, i, a, o, s, c = e.length;
	for (r = 0; r < c; r++) {
		let c = e[r];
		if (c !== 0) {
			if (i = n[n.length - 1], e[i] < c) {
				t[r] = i, n.push(r);
				continue;
			}
			for (a = 0, o = n.length - 1; a < o;) s = a + o >> 1, e[n[s]] < c ? a = s + 1 : o = s;
			c < e[n[a]] && (a > 0 && (t[r] = n[a - 1]), n[a] = r);
		}
	}
	for (a = n.length, o = n[a - 1]; a-- > 0;) n[a] = o, o = t[o];
	return n;
}
function Ki(e) {
	let t = e.subTree.component;
	if (t) return t.asyncDep && !t.asyncResolved ? t : Ki(t);
}
function qi(e) {
	if (e) for (let t = 0; t < e.length; t++) e[t].flags |= 8;
}
function Ji(e) {
	if (e.placeholder) return e.placeholder;
	let t = e.component;
	return t ? Ji(t.subTree) : null;
}
var Yi = (e) => e.__isSuspense;
function Xi(e, t) {
	t && t.pendingBranch ? M(e) ? t.effects.push(...e) : t.effects.push(e) : Un(e);
}
var Zi = /* @__PURE__ */ Symbol.for("v-fgt"), Qi = /* @__PURE__ */ Symbol.for("v-txt"), $i = /* @__PURE__ */ Symbol.for("v-cmt"), ea = /* @__PURE__ */ Symbol.for("v-stc"), ta = [], na = null;
function K(e = !1) {
	ta.push(na = e ? null : []);
}
function ra() {
	ta.pop(), na = ta[ta.length - 1] || null;
}
var ia = 1;
function aa(e, t = !1) {
	ia += e, e < 0 && na && t && (na.hasOnce = !0);
}
function oa(e) {
	return e.dynamicChildren = ia > 0 ? na || te : null, ra(), ia > 0 && na && na.push(e), e;
}
function q(e, t, n, r, i, a) {
	return oa(J(e, t, n, r, i, a, !0));
}
function sa(e, t, n, r, i) {
	return oa(fa(e, t, n, r, i, !0));
}
function ca(e) {
	return e ? e.__v_isVNode === !0 : !1;
}
function la(e, t) {
	return e.type === t.type && e.key === t.key;
}
var ua = ({ key: e }) => e ?? null, da = ({ ref: e, ref_key: t, ref_for: n }) => (typeof e == "number" && (e = "" + e), e == null ? null : P(e) || /* @__PURE__ */ hn(e) || N(e) ? {
	i: Jn,
	r: e,
	k: t,
	f: !!n
} : e);
function J(e, t = null, n = null, r = 0, i = null, a = e === Zi ? 0 : 1, o = !1, s = !1) {
	let c = {
		__v_isVNode: !0,
		__v_skip: !0,
		type: e,
		props: t,
		key: t && ua(t),
		ref: t && da(t),
		scopeId: Yn,
		slotScopeIds: null,
		children: n,
		component: null,
		suspense: null,
		ssContent: null,
		ssFallback: null,
		dirs: null,
		transition: null,
		el: null,
		anchor: null,
		target: null,
		targetStart: null,
		targetAnchor: null,
		staticCount: 0,
		shapeFlag: a,
		patchFlag: r,
		dynamicProps: i,
		dynamicChildren: null,
		appContext: null,
		ctx: Jn
	};
	return s ? (ba(c, n), a & 128 && e.normalize(c)) : n && (c.shapeFlag |= P(n) ? 8 : 16), ia > 0 && !o && na && (c.patchFlag > 0 || a & 6) && c.patchFlag !== 32 && na.push(c), c;
}
var fa = pa;
function pa(e, t = null, n = null, r = 0, i = null, a = !1) {
	if ((!e || e === Ir) && (e = $i), ca(e)) {
		let r = ha(e, t, !0);
		return n && ba(r, n), ia > 0 && !a && na && (r.shapeFlag & 6 ? na[na.indexOf(e)] = r : na.push(r)), r.patchFlag = -2, r;
	}
	if (Ua(e) && (e = e.__vccOpts), t) {
		t = ma(t);
		let { class: e, style: n } = t;
		e && !P(e) && (t.class = Me(e)), F(n) && (/* @__PURE__ */ dn(n) && !M(n) && (n = A({}, n)), t.style = De(n));
	}
	let o = P(e) ? 1 : Yi(e) ? 128 : cr(e) ? 64 : F(e) ? 4 : N(e) ? 2 : 0;
	return J(e, t, n, r, i, o, a, !0);
}
function ma(e) {
	return e ? /* @__PURE__ */ dn(e) || Si(e) ? A({}, e) : e : null;
}
function ha(e, t, n = !1, r = !1) {
	let { props: i, ref: a, patchFlag: o, children: s, transition: c } = e, l = t ? xa(i || {}, t) : i, u = {
		__v_isVNode: !0,
		__v_skip: !0,
		type: e.type,
		props: l,
		key: l && ua(l),
		ref: t && t.ref ? n && a ? M(a) ? a.concat(da(t)) : [a, da(t)] : da(t) : a,
		scopeId: e.scopeId,
		slotScopeIds: e.slotScopeIds,
		children: s,
		target: e.target,
		targetStart: e.targetStart,
		targetAnchor: e.targetAnchor,
		staticCount: e.staticCount,
		shapeFlag: e.shapeFlag,
		patchFlag: t && e.type !== Zi ? o === -1 ? 16 : o | 16 : o,
		dynamicProps: e.dynamicProps,
		dynamicChildren: e.dynamicChildren,
		appContext: e.appContext,
		dirs: e.dirs,
		transition: c,
		component: e.component,
		suspense: e.suspense,
		ssContent: e.ssContent && ha(e.ssContent),
		ssFallback: e.ssFallback && ha(e.ssFallback),
		placeholder: e.placeholder,
		el: e.el,
		anchor: e.anchor,
		ctx: e.ctx,
		ce: e.ce
	};
	return c && r && ur(u, c.clone(u)), u;
}
function ga(e = " ", t = 0) {
	return fa(Qi, null, e, t);
}
function _a(e = "", t = !1) {
	return t ? (K(), sa($i, null, e)) : fa($i, null, e);
}
function va(e) {
	return e == null || typeof e == "boolean" ? fa($i) : M(e) ? fa(Zi, null, e.slice()) : ca(e) ? ya(e) : fa(Qi, null, String(e));
}
function ya(e) {
	return e.el === null && e.patchFlag !== -1 || e.memo ? e : ha(e);
}
function ba(e, t) {
	let n = 0, { shapeFlag: r } = e;
	if (t == null) t = null;
	else if (M(t)) n = 16;
	else if (typeof t == "object") if (r & 65) {
		let n = t.default;
		n && (n._c && (n._d = !1), ba(e, n()), n._c && (n._d = !0));
		return;
	} else {
		n = 32;
		let r = t._;
		!r && !Si(t) ? t._ctx = Jn : r === 3 && Jn && (Jn.slots._ === 1 ? t._ = 1 : (t._ = 2, e.patchFlag |= 1024));
	}
	else if (N(t)) {
		if (r & 65) {
			ba(e, { default: t });
			return;
		}
		t = {
			default: t,
			_ctx: Jn
		}, n = 32;
	} else t = String(t), r & 64 ? (n = 16, t = [ga(t)]) : n = 8;
	e.children = t, e.shapeFlag |= n;
}
function xa(...e) {
	let t = {};
	for (let n = 0; n < e.length; n++) {
		let r = e[n];
		for (let e in r) if (e === "class") t.class !== r.class && (t.class = Me([t.class, r.class]));
		else if (e === "style") t.style = De([t.style, r.style]);
		else if (O(e)) {
			let n = t[e], i = r[e];
			i && n !== i && !(M(n) && n.includes(i)) ? t[e] = n ? [].concat(n, i) : i : i == null && n == null && !k(e) && (t[e] = i);
		} else e !== "" && (t[e] = r[e]);
	}
	return t;
}
function Sa(e, t, n, r = null) {
	kn(e, t, 7, [n, r]);
}
var Ca = ii(), wa = 0;
function Ta(e, t, n) {
	let r = e.type, i = (t ? t.appContext : e.appContext) || Ca, a = {
		uid: wa++,
		vnode: e,
		type: r,
		parent: t,
		appContext: i,
		root: null,
		next: null,
		subTree: null,
		effect: null,
		update: null,
		job: null,
		scope: new He(!0),
		render: null,
		proxy: null,
		exposed: null,
		exposeProxy: null,
		withProxy: null,
		provides: t ? t.provides : Object.create(i.provides),
		ids: t ? t.ids : [
			"",
			0,
			0
		],
		accessCache: null,
		renderCache: [],
		components: null,
		directives: null,
		propsOptions: Oi(r, i),
		emitsOptions: di(r, i),
		emit: null,
		emitted: null,
		propsDefaults: E,
		inheritAttrs: r.inheritAttrs,
		ctx: E,
		data: E,
		props: E,
		attrs: E,
		slots: E,
		refs: E,
		setupState: E,
		setupContext: null,
		suspense: n,
		suspenseId: n ? n.pendingId : 0,
		asyncDep: null,
		asyncResolved: !1,
		isMounted: !1,
		isUnmounted: !1,
		isDeactivated: !1,
		bc: null,
		c: null,
		bm: null,
		m: null,
		bu: null,
		u: null,
		um: null,
		bum: null,
		da: null,
		a: null,
		rtg: null,
		rtc: null,
		ec: null,
		sp: null
	};
	return a.ctx = { _: a }, a.root = t ? t.root : a, a.emit = li.bind(null, a), e.ce && e.ce(a), a;
}
var Ea = null, Da = () => Ea || Jn, Oa, ka;
{
	let e = Ee(), t = (t, n) => {
		let r;
		return (r = e[t]) || (r = e[t] = []), r.push(n), (e) => {
			r.length > 1 ? r.forEach((t) => t(e)) : r[0](e);
		};
	};
	Oa = t("__VUE_INSTANCE_SETTERS__", (e) => Ea = e), ka = t("__VUE_SSR_SETTERS__", (e) => Na = e);
}
var Aa = (e) => {
	let t = Ea;
	return Oa(e), e.scope.on(), () => {
		e.scope.off(), Oa(t);
	};
}, ja = () => {
	Ea && Ea.scope.off(), Oa(null);
};
function Ma(e) {
	return e.vnode.shapeFlag & 4;
}
var Na = !1;
function Pa(e, t = !1, n = !1) {
	t && ka(t);
	let { props: r, children: i } = e.vnode, a = Ma(e);
	Ci(e, r, a, t), Ii(e, i, n || t);
	let o = a ? Fa(e, t) : void 0;
	return t && ka(!1), o;
}
function Fa(e, t) {
	let n = e.type;
	e.accessCache = /* @__PURE__ */ Object.create(null), e.proxy = new Proxy(e.ctx, Vr);
	let { setup: r } = n;
	if (r) {
		ct();
		let n = e.setupContext = r.length > 1 ? Va(e) : null, i = Aa(e), a = On(r, e, 0, [e.props, n]), o = le(a);
		if (lt(), i(), (o || e.sp) && !vr(e) && fr(e), o) {
			if (a.then(ja, ja), t) return a.then((n) => {
				Ia(e, n, t);
			}).catch((t) => {
				An(t, e, 0);
			});
			e.asyncDep = a;
		} else Ia(e, a, t);
	} else za(e, t);
}
function Ia(e, t, n) {
	N(t) ? e.type.__ssrInlineRender ? e.ssrRender = t : e.render = t : F(t) && (e.setupState = yn(t)), za(e, n);
}
var La, Ra;
function za(e, t, n) {
	let r = e.type;
	if (!e.render) {
		if (!t && La && !r.render) {
			let t = r.template || Jr(e).template;
			if (t) {
				let { isCustomElement: n, compilerOptions: i } = e.appContext.config, { delimiters: a, compilerOptions: o } = r;
				r.render = La(t, A(A({
					isCustomElement: n,
					delimiters: a
				}, i), o));
			}
		}
		e.render = r.render || D, Ra && Ra(e);
	}
	{
		let t = Aa(e);
		ct();
		try {
			Wr(e);
		} finally {
			lt(), t();
		}
	}
}
var Ba = { get(e, t) {
	return yt(e, "get", ""), e[t];
} };
function Va(e) {
	return {
		attrs: new Proxy(e.attrs, Ba),
		slots: e.slots,
		emit: e.emit,
		expose: (t) => {
			e.exposed = t || {};
		}
	};
}
function Ha(e) {
	return e.exposed ? e.exposeProxy ||= new Proxy(yn(fn(e.exposed)), {
		get(t, n) {
			if (n in t) return t[n];
			if (n in zr) return zr[n](e);
		},
		has(e, t) {
			return t in e || t in zr;
		}
	}) : e.proxy;
}
function Ua(e) {
	return N(e) && "__vccOpts" in e;
}
var Y = (e, t) => /* @__PURE__ */ xn(e, t, Na), Wa = "3.5.40", Ga = void 0, Ka = typeof window < "u" && window.trustedTypes;
if (Ka) try {
	Ga = /* @__PURE__ */ Ka.createPolicy("vue", { createHTML: (e) => e });
} catch {}
var qa = Ga ? (e) => Ga.createHTML(e) : (e) => e, Ja = "http://www.w3.org/2000/svg", Ya = "http://www.w3.org/1998/Math/MathML", Xa = typeof document < "u" ? document : null, Za = Xa && /* @__PURE__ */ Xa.createElement("template"), Qa = {
	insert: (e, t, n) => {
		t.insertBefore(e, n || null);
	},
	remove: (e) => {
		let t = e.parentNode;
		t && t.removeChild(e);
	},
	createElement: (e, t, n, r) => {
		let i = t === "svg" ? Xa.createElementNS(Ja, e) : t === "mathml" ? Xa.createElementNS(Ya, e) : n ? Xa.createElement(e, { is: n }) : Xa.createElement(e);
		return e === "select" && r && r.multiple != null && i.setAttribute("multiple", r.multiple), i;
	},
	createText: (e) => Xa.createTextNode(e),
	createComment: (e) => Xa.createComment(e),
	setText: (e, t) => {
		e.nodeValue = t;
	},
	setElementText: (e, t) => {
		e.textContent = t;
	},
	parentNode: (e) => e.parentNode,
	nextSibling: (e) => e.nextSibling,
	querySelector: (e) => Xa.querySelector(e),
	setScopeId(e, t) {
		e.setAttribute(t, "");
	},
	insertStaticContent(e, t, n, r, i, a) {
		let o = n ? n.previousSibling : t.lastChild;
		if (i && (i === a || i.nextSibling)) for (; t.insertBefore(i.cloneNode(!0), n), !(i === a || !(i = i.nextSibling)););
		else {
			Za.innerHTML = qa(r === "svg" ? `<svg>${e}</svg>` : r === "mathml" ? `<math>${e}</math>` : e);
			let i = Za.content;
			if (r === "svg" || r === "mathml") {
				let e = i.firstChild;
				for (; e.firstChild;) i.appendChild(e.firstChild);
				i.removeChild(e);
			}
			t.insertBefore(i, n);
		}
		return [o ? o.nextSibling : t.firstChild, n ? n.previousSibling : t.lastChild];
	}
}, $a = /* @__PURE__ */ Symbol("_vtc");
function eo(e, t, n) {
	let r = e[$a];
	r && (t = (t ? [t, ...r] : [...r]).join(" ")), t == null ? e.removeAttribute("class") : n ? e.setAttribute("class", t) : e.className = t;
}
var to = /* @__PURE__ */ Symbol("_vod"), no = /* @__PURE__ */ Symbol("_vsh"), ro = /* @__PURE__ */ Symbol(""), io = /(?:^|;)\s*display\s*:/;
function ao(e, t, n) {
	let r = e.style, i = P(n), a = !1;
	if (n && !i) {
		if (t) if (P(t)) for (let e of t.split(";")) {
			let t = e.slice(0, e.indexOf(":")).trim();
			n[t] ?? so(r, t, "");
		}
		else for (let e in t) n[e] ?? so(r, e, "");
		for (let i in n) {
			i === "display" && (a = !0);
			let o = n[i];
			o == null ? so(r, i, "") : fo(e, i, !P(t) && t ? t[i] : void 0, o) || so(r, i, o);
		}
	} else if (i) {
		if (t !== n) {
			let e = r[ro];
			e && (n += ";" + e), r.cssText = n, a = io.test(n);
		}
	} else t && e.removeAttribute("style");
	to in e && (e[to] = a ? r.display : "", e[no] && (r.display = "none"));
}
var oo = /\s*!important$/;
function so(e, t, n) {
	if (M(n)) n.forEach((n) => so(e, t, n));
	else if (n ??= "", t.startsWith("--")) e.setProperty(t, n);
	else {
		let r = uo(e, t);
		oo.test(n) ? e.setProperty(ve(r), n.replace(oo, ""), "important") : e[r] = n;
	}
}
var co = [
	"Webkit",
	"Moz",
	"ms"
], lo = {};
function uo(e, t) {
	let n = lo[t];
	if (n) return n;
	let r = L(t);
	if (r !== "filter" && r in e) return lo[t] = r;
	r = ye(r);
	for (let n = 0; n < co.length; n++) {
		let i = co[n] + r;
		if (i in e) return lo[t] = i;
	}
	return t;
}
function fo(e, t, n, r) {
	return e.tagName === "TEXTAREA" && (t === "width" || t === "height") && P(r) && n === r;
}
var po = "http://www.w3.org/1999/xlink";
function mo(e, t, n, r, i, a = Pe(t)) {
	r && t.startsWith("xlink:") ? n == null ? e.removeAttributeNS(po, t.slice(6, t.length)) : e.setAttributeNS(po, t, n) : n == null || a && !Fe(n) ? e.removeAttribute(t) : e.setAttribute(t, a ? "" : ce(n) ? String(n) : n);
}
function ho(e, t, n, r, i) {
	if (t === "innerHTML" || t === "textContent") {
		n != null && (e[t] = t === "innerHTML" ? qa(n) : n);
		return;
	}
	let a = e.tagName;
	if (t === "value" && a !== "PROGRESS" && !a.includes("-")) {
		let r = a === "OPTION" ? e.getAttribute("value") || "" : e.value, i = n == null ? e.type === "checkbox" ? "on" : "" : String(n);
		(r !== i || !("_value" in e)) && (e.value = i), n ?? e.removeAttribute(t), e._value = n;
		return;
	}
	let o = !1;
	if (n === "" || n == null) {
		let r = typeof e[t];
		r === "boolean" ? n = Fe(n) : n == null && r === "string" ? (n = "", o = !0) : r === "number" && (n = 0, o = !0);
	}
	try {
		e[t] = n;
	} catch {}
	o && e.removeAttribute(i || t);
}
function go(e, t, n, r) {
	e.addEventListener(t, n, r);
}
function _o(e, t, n, r) {
	e.removeEventListener(t, n, r);
}
var vo = /* @__PURE__ */ Symbol("_vei");
function yo(e, t, n, r, i = null) {
	let a = e[vo] || (e[vo] = {}), o = a[t];
	if (r && o) o.value = r;
	else {
		let [n, s] = So(t);
		r ? go(e, n, a[t] = Eo(r, i), s) : o && (_o(e, n, o, s), a[t] = void 0);
	}
}
var bo = /(Once|Passive|Capture)$/, xo = /^on:?(?:Once|Passive|Capture)$/;
function So(e) {
	let t, n;
	for (; (n = e.match(bo)) && !xo.test(e);) t ||= {}, e = e.slice(0, e.length - n[1].length), t[n[1].toLowerCase()] = !0;
	return [e[2] === ":" ? e.slice(3) : ve(e.slice(2)), t];
}
var Co = 0, wo = /* @__PURE__ */ Promise.resolve(), To = () => Co ||= (wo.then(() => Co = 0), Date.now());
function Eo(e, t) {
	let n = (e) => {
		if (!e._vts) e._vts = Date.now();
		else if (e._vts <= n.attached) return;
		let r = n.value;
		if (M(r)) {
			let n = e.stopImmediatePropagation;
			e.stopImmediatePropagation = () => {
				n.call(e), e._stopped = !0;
			};
			let i = r.slice(), a = [e];
			for (let n = 0; n < i.length && !e._stopped; n++) {
				let e = i[n];
				e && kn(e, t, 5, a);
			}
		} else kn(r, t, 5, [e]);
	};
	return n.value = e, n.attached = To(), n;
}
var Do = (e) => e.charCodeAt(0) === 111 && e.charCodeAt(1) === 110 && e.charCodeAt(2) > 96 && e.charCodeAt(2) < 123, Oo = (e, t, n, r, i, a) => {
	let o = i === "svg";
	t === "class" ? eo(e, r, o) : t === "style" ? ao(e, n, r) : O(t) ? k(t) || yo(e, t, n, r, a) : (t[0] === "." ? (t = t.slice(1), !0) : t[0] === "^" ? (t = t.slice(1), !1) : ko(e, t, r, o)) ? (ho(e, t, r), !e.tagName.includes("-") && (t === "value" || t === "checked" || t === "selected") && mo(e, t, r, o, a, t !== "value")) : e._isVueCE && (Ao(e, t) || e._def.__asyncLoader && (/[A-Z]/.test(t) || !P(r))) ? ho(e, L(t), r, a, t) : (t === "true-value" ? e._trueValue = r : t === "false-value" && (e._falseValue = r), mo(e, t, r, o));
};
function ko(e, t, n, r) {
	if (r) return !!(t === "innerHTML" || t === "textContent" || t in e && Do(t) && N(n));
	if (t === "spellcheck" || t === "draggable" || t === "translate" || t === "autocorrect" || t === "sandbox" && e.tagName === "IFRAME" || t === "form" || t === "list" && e.tagName === "INPUT" || t === "type" && e.tagName === "TEXTAREA") return !1;
	if (t === "width" || t === "height") {
		let t = e.tagName;
		if (t === "IMG" || t === "VIDEO" || t === "CANVAS" || t === "SOURCE") return !1;
	}
	return Do(t) && P(n) ? !1 : t in e;
}
function Ao(e, t) {
	let n = e._def.props;
	if (!n) return !1;
	let r = L(t);
	return Array.isArray(n) ? n.some((e) => L(e) === r) : Object.keys(n).some((e) => L(e) === r);
}
var jo = /* @__PURE__ */ A({ patchProp: Oo }, Qa), Mo;
function No() {
	return Mo ||= zi(jo);
}
var Po = ((...e) => {
	let t = No().createApp(...e), { mount: n } = t;
	return t.mount = (e) => {
		let r = Io(e);
		if (!r) return;
		let i = t._component;
		!N(i) && !i.render && !i.template && (i.template = r.innerHTML), r.nodeType === 1 && (r.textContent = "");
		let a = n(r, !1, Fo(r));
		return r instanceof Element && (r.removeAttribute("v-cloak"), r.setAttribute("data-v-app", "")), a;
	}, t;
});
function Fo(e) {
	if (e instanceof SVGElement) return "svg";
	if (typeof MathMLElement == "function" && e instanceof MathMLElement) return "mathml";
}
function Io(e) {
	return P(e) ? document.querySelector(e) : e;
}
//#endregion
//#region node_modules/@vueuse/shared/dist/index.js
function Lo(e, t) {
	return We() ? (Ge(e, t), !0) : !1;
}
var Ro = typeof window < "u" && typeof document < "u";
typeof WorkerGlobalScope < "u" && globalThis instanceof WorkerGlobalScope;
var zo = Object.prototype.toString, Bo = (e) => zo.call(e) === "[object Object]", Vo = () => +Date.now();
function Ho(e) {
	return Array.isArray(e) ? e : [e];
}
function Uo(e) {
	return e || Da();
}
function Wo(e, t = !0, n) {
	Uo(n) ? Dr(e, n) : t ? e() : zn(e);
}
function Go(e, t = 1e3, n = {}) {
	let { immediate: r = !0, immediateCallback: i = !1 } = n, a = null, o = /* @__PURE__ */ H(!1);
	function s() {
		a &&= (clearInterval(a), null);
	}
	function c() {
		o.value = !1, s();
	}
	function l() {
		let n = W(t);
		n <= 0 || (o.value = !0, i && e(), s(), o.value && (a = setInterval(e, n)));
	}
	return r && Ro && l(), (/* @__PURE__ */ hn(t) || typeof t == "function") && Lo(G(t, () => {
		o.value && Ro && l();
	})), Lo(c), {
		isActive: /* @__PURE__ */ on(o),
		pause: c,
		resume: l
	};
}
function Ko(e, t, n = {}) {
	let { immediate: r = !0, immediateCallback: i = !1 } = n, a = /* @__PURE__ */ H(!1), o;
	function s() {
		o &&= (clearTimeout(o), void 0);
	}
	function c() {
		a.value = !1, s();
	}
	function l(...n) {
		i && e(), s(), a.value = !0, o = setTimeout(() => {
			a.value = !1, o = void 0, e(...n);
		}, W(t));
	}
	return r && (a.value = !0, Ro && l()), Lo(c), {
		isPending: /* @__PURE__ */ on(a),
		start: l,
		stop: c
	};
}
function qo(e, t, n) {
	return G(e, t, {
		...n,
		immediate: !0
	});
}
function Jo(e, t, n) {
	let r = G(e, (e, i, a) => {
		e && (n?.once && zn(() => r()), t(e, i, a));
	}, {
		...n,
		once: !1
	});
	return r;
}
//#endregion
//#region node_modules/@vueuse/core/dist/index.js
var Yo = Ro ? window : void 0;
Ro && window.document, Ro && window.navigator, Ro && window.location;
function Xo(e) {
	let t = W(e);
	return t?.$el ?? t;
}
function Zo(...e) {
	let t = (e, t, n, r) => (e.addEventListener(t, n, r), () => e.removeEventListener(t, n, r)), n = Y(() => {
		let t = Ho(W(e[0])).filter((e) => e != null);
		return t.every((e) => typeof e != "string") ? t : void 0;
	});
	return qo(() => [
		n.value?.map((e) => Xo(e)) ?? [Yo].filter((e) => e != null),
		Ho(W(n.value ? e[1] : e[0])),
		Ho(U(n.value ? e[2] : e[1])),
		W(n.value ? e[3] : e[2])
	], ([e, n, r, i], a, o) => {
		if (!e?.length || !n?.length || !r?.length) return;
		let s = Bo(i) ? { ...i } : i, c = e.flatMap((e) => n.flatMap((n) => r.map((r) => t(e, n, r, s))));
		o(() => {
			c.forEach((e) => e());
		});
	}, { flush: "post" });
}
function Qo() {
	let e = /* @__PURE__ */ H(!1), t = Da();
	return t && Dr(() => {
		e.value = !0;
	}, t), e;
}
/* @__NO_SIDE_EFFECTS__ */
function $o(e) {
	let t = Qo();
	return Y(() => (t.value, !!e()));
}
function es(e, t = {}) {
	let { immediate: n = !0, fpsLimit: r = null, window: i = Yo, once: a = !1 } = t, o = /* @__PURE__ */ H(!1), s = Y(() => {
		let e = W(r);
		return e ? 1e3 / e : null;
	}), c = 0, l = null;
	function u(t) {
		if (!o.value || !i) return;
		c ||= t;
		let n = t - c;
		if (s.value && n < s.value) {
			l = i.requestAnimationFrame(u);
			return;
		}
		if (c = t, e({
			delta: n,
			timestamp: t
		}), a) {
			o.value = !1, l = null;
			return;
		}
		l = i.requestAnimationFrame(u);
	}
	function d() {
		!o.value && i && (o.value = !0, c = 0, l = i.requestAnimationFrame(u));
	}
	function f() {
		o.value = !1, l != null && i && (i.cancelAnimationFrame(l), l = null);
	}
	return n && d(), Lo(f), {
		isActive: /* @__PURE__ */ on(o),
		pause: f,
		resume: d
	};
}
function ts(e, t, n = {}) {
	let { window: r = Yo, ...i } = n, a, o = /* @__PURE__ */ $o(() => r && "ResizeObserver" in r), s = () => {
		a &&= (a.disconnect(), void 0);
	}, c = G(Y(() => {
		let t = W(e);
		return Array.isArray(t) ? t.map((e) => Xo(e)) : [Xo(t)];
	}), (e) => {
		if (s(), o.value && r) {
			a = new ResizeObserver(t);
			for (let t of e) t && a.observe(t, i);
		}
	}, {
		immediate: !0,
		flush: "post"
	}), l = () => {
		s(), c();
	};
	return Lo(l), {
		isSupported: o,
		stop: l
	};
}
function ns(e, t = {
	width: 0,
	height: 0
}, n = {}) {
	let { window: r = Yo, box: i = "content-box" } = n, a = Y(() => {
		var t;
		return (t = Xo(e)) == null || (t = t.namespaceURI) == null ? void 0 : t.includes("svg");
	}), o = /* @__PURE__ */ H(t.width), s = /* @__PURE__ */ H(t.height), { stop: c } = ts(e, ([t]) => {
		let n = i === "border-box" ? t.borderBoxSize : i === "content-box" ? t.contentBoxSize : t.devicePixelContentBoxSize;
		if (r && a.value) {
			let t = Xo(e);
			if (t) {
				let e = t.getBoundingClientRect();
				o.value = e.width, s.value = e.height;
			}
		} else if (n) {
			let e = Ho(n);
			o.value = e.reduce((e, { inlineSize: t }) => e + t, 0), s.value = e.reduce((e, { blockSize: t }) => e + t, 0);
		} else o.value = t.contentRect.width, s.value = t.contentRect.height;
	}, n);
	Wo(() => {
		let n = Xo(e);
		if (n && "offsetWidth" in n) if (i === "content-box" && r) {
			let e = r.getComputedStyle(n), t = Number.parseFloat(e.paddingLeft) + Number.parseFloat(e.paddingRight), i = Number.parseFloat(e.paddingTop) + Number.parseFloat(e.paddingBottom), a = Number.parseFloat(e.borderLeftWidth) + Number.parseFloat(e.borderRightWidth), c = Number.parseFloat(e.borderTopWidth) + Number.parseFloat(e.borderBottomWidth);
			o.value = n.offsetWidth - t - a, s.value = n.offsetHeight - i - c;
		} else o.value = n.offsetWidth, s.value = n.offsetHeight;
		else n && (o.value = t.width, s.value = t.height);
	});
	let l = G(() => Xo(e), (e) => {
		o.value = e ? t.width : 0, s.value = e ? t.height : 0;
	});
	function u() {
		c(), l();
	}
	return {
		width: o,
		height: s,
		stop: u
	};
}
function rs(e) {
	if ("interval" in e || "immediate" in e) {
		let { interval: t = "requestAnimationFrame", immediate: n = !0 } = e;
		return t === "requestAnimationFrame" ? (e) => es(e, { immediate: n }) : (e) => Go(e, t, { immediate: n });
	}
	return es;
}
function is(e = {}) {
	let { controls: t = !1, offset: n = 0, scheduler: r = rs(e), callback: i } = e, a = /* @__PURE__ */ H(Vo() + n), o = () => a.value = Vo() + n, s = r(i ? () => {
		o(), i(a.value);
	} : o);
	return t ? {
		timestamp: a,
		...s
	} : a;
}
//#endregion
//#region ../../sdk/node/dist/plugin/api.js
var as;
(function(e) {
	e.FINISH_LAUNCHING = "finishLaunching", e.SHUTDOWN = "shutdown";
})(as ||= {});
//#endregion
//#region ../../sdk/node/dist/plugin/contract.js
var os;
(function(e) {
	e.Hub = "hub", e.SensorProvider = "sensorProvider", e.CameraController = "cameraController", e.CameraAndSensorProvider = "cameraAndSensorProvider";
})(os ||= {});
var ss;
(function(e) {
	e.MotionDetection = "MotionDetection", e.ObjectDetection = "ObjectDetection", e.AudioDetection = "AudioDetection", e.FaceDetection = "FaceDetection", e.LicensePlateDetection = "LicensePlateDetection", e.ClassifierDetection = "ClassifierDetection", e.ClipDetection = "ClipDetection", e.DiscoveryProvider = "DiscoveryProvider", e.NVR = "NVR", e.Notifier = "Notifier", e.OAuthCapable = "OAuthCapable", e.OAuthDeviceFlow = "OAuthDeviceFlow", e.OAuthAuthCodeFlow = "OAuthAuthCodeFlow", e.OAuthClientCredentials = "OAuthClientCredentials";
})(ss ||= {});
var cs;
(function(e) {
	e.PublishNotifications = "publishNotifications";
})(cs ||= {});
//#endregion
//#region ../../sdk/node/dist/sensor/base.js
var X;
(function(e) {
	e.Motion = "motion", e.Object = "object", e.Audio = "audio", e.Face = "face", e.LicensePlate = "licensePlate", e.Classifier = "classifier", e.Clip = "clip", e.ObjectAssist = "objectAssist", e.Contact = "contact", e.Temperature = "temperature", e.Humidity = "humidity", e.Occupancy = "occupancy", e.Smoke = "smoke", e.Leak = "leak", e.Gas = "gas", e.CarbonMonoxide = "carbonMonoxide", e.Heat = "heat", e.Cold = "cold", e.Vibration = "vibration", e.Tamper = "tamper", e.Problem = "problem", e.Power = "power", e.Illuminance = "illuminance", e.CarbonDioxide = "carbonDioxide", e.Light = "light", e.Siren = "siren", e.Switch = "switch", e.Lock = "lock", e.PTZ = "ptz", e.SecuritySystem = "securitySystem", e.Garage = "garage", e.Doorbell = "doorbell", e.Battery = "battery";
})(X ||= {});
var Z;
(function(e) {
	e.Sensor = "sensor", e.Control = "control", e.Trigger = "trigger", e.Info = "info";
})(Z ||= {});
//#endregion
//#region ../../sdk/node/dist/plugin/notifier.js
var ls;
(function(e) {
	e.Info = "info", e.Warn = "warn", e.Error = "error", e.Critical = "critical";
})(ls ||= {});
//#endregion
//#region ../../sdk/node/dist/sensor/meta.js
var Q;
(function(e) {
	e.Binary = "binary", e.Measurement = "measurement", e.Switch = "switch", e.Light = "light", e.Siren = "siren", e.Lock = "lock", e.Cover = "cover", e.Alarm = "alarm";
})(Q ||= {});
//#endregion
//#region ../../sdk/node/dist/sensor/audio.js
var us;
(function(e) {
	e.Detected = "detected", e.Detections = "detections", e.Decibels = "decibels", e.LastTriggered = "lastTriggered";
})(us ||= {}), X.Audio, Z.Sensor, us.Detected, us.Detections, us.Decibels, us.LastTriggered;
//#endregion
//#region ../../sdk/node/dist/sensor/battery.js
var ds;
(function(e) {
	e.LowBattery = "lowBattery", e.Charging = "charging";
})(ds ||= {});
var fs;
(function(e) {
	e.Level = "level", e.Charging = "charging", e.Low = "low";
})(fs ||= {});
var ps;
(function(e) {
	e.NotChargeable = "NOT_CHARGEABLE", e.NotCharging = "NOT_CHARGING", e.Charging = "CHARGING", e.Full = "FULL";
})(ps ||= {}), X.Battery, Z.Info, fs.Level, fs.Charging, ps.NotChargeable, ps.NotCharging, ps.Charging, ps.Full, fs.Low, fs.Charging, ds.Charging, fs.Low, ds.LowBattery, Q.Measurement, fs.Level, fs.Level;
//#endregion
//#region ../../sdk/node/dist/sensor/carbonDioxide.js
var ms;
(function(e) {
	e.Current = "current";
})(ms ||= {}), X.CarbonDioxide, Z.Info, ms.Current, ms.Current, Q.Measurement, ms.Current, ms.Current;
//#endregion
//#region ../../sdk/node/dist/sensor/carbonMonoxide.js
var hs;
(function(e) {
	e.Detected = "detected";
})(hs ||= {}), X.CarbonMonoxide, Z.Sensor, hs.Detected, hs.Detected, hs.Detected, Q.Binary, hs.Detected, hs.Detected;
//#endregion
//#region ../../sdk/node/dist/sensor/classifier.js
var gs;
(function(e) {
	e.Detected = "detected", e.Detections = "detections", e.Labels = "labels";
})(gs ||= {}), X.Classifier, Z.Sensor, gs.Detected, gs.Detections, gs.Labels, X.Clip, Z.Sensor;
//#endregion
//#region ../../sdk/node/dist/sensor/cold.js
var _s;
(function(e) {
	e.Detected = "detected";
})(_s ||= {}), X.Cold, Z.Sensor, _s.Detected, _s.Detected, _s.Detected, Q.Binary, _s.Detected, _s.Detected;
//#endregion
//#region ../../sdk/node/dist/sensor/contact.js
var vs;
(function(e) {
	e.Detected = "detected";
})(vs ||= {}), X.Contact, Z.Sensor, vs.Detected, vs.Detected, vs.Detected, Q.Binary, vs.Detected, vs.Detected;
//#endregion
//#region ../../sdk/node/dist/sensor/doorbell.js
var ys;
(function(e) {
	e.Ring = "ring";
})(ys ||= {}), X.Doorbell, Z.Trigger, ys.Ring, ys.Ring, ys.Ring, Q.Binary, ys.Ring, ys.Ring;
//#endregion
//#region ../../sdk/node/dist/sensor/face.js
var bs;
(function(e) {
	e.Detected = "detected", e.Detections = "detections";
})(bs ||= {}), X.Face, Z.Sensor, bs.Detected, bs.Detections;
//#endregion
//#region ../../sdk/node/dist/sensor/garage.js
var xs;
(function(e) {
	e[e.Open = 0] = "Open", e[e.Closed = 1] = "Closed", e[e.Opening = 2] = "Opening", e[e.Closing = 3] = "Closing", e[e.Stopped = 4] = "Stopped";
})(xs ||= {});
var Ss;
(function(e) {
	e.CurrentState = "currentState", e.TargetState = "targetState", e.ObstructionDetected = "obstructionDetected";
})(Ss ||= {}), X.Garage, Z.Control, Ss.CurrentState, xs.Open, xs.Closed, xs.Opening, xs.Closing, xs.Stopped, Ss.TargetState, xs.Open, xs.Closed, Ss.ObstructionDetected, Ss.CurrentState, Ss.CurrentState, Ss.TargetState, Q.Cover, Ss.CurrentState, Ss.TargetState, xs.Open, xs.Closed, xs.Opening, xs.Closing, xs.Stopped;
//#endregion
//#region ../../sdk/node/dist/sensor/gas.js
var Cs;
(function(e) {
	e.Detected = "detected";
})(Cs ||= {}), X.Gas, Z.Sensor, Cs.Detected, Cs.Detected, Cs.Detected, Q.Binary, Cs.Detected, Cs.Detected;
//#endregion
//#region ../../sdk/node/dist/sensor/heat.js
var ws;
(function(e) {
	e.Detected = "detected";
})(ws ||= {}), X.Heat, Z.Sensor, ws.Detected, ws.Detected, ws.Detected, Q.Binary, ws.Detected, ws.Detected;
//#endregion
//#region ../../sdk/node/dist/sensor/humidity.js
var Ts;
(function(e) {
	e.Current = "current";
})(Ts ||= {}), X.Humidity, Z.Info, Ts.Current, Ts.Current, Q.Measurement, Ts.Current, Ts.Current;
//#endregion
//#region ../../sdk/node/dist/sensor/illuminance.js
var Es;
(function(e) {
	e.Current = "current";
})(Es ||= {}), X.Illuminance, Z.Info, Es.Current, Es.Current, Q.Measurement, Es.Current, Es.Current;
//#endregion
//#region ../../sdk/node/dist/sensor/leak.js
var Ds;
(function(e) {
	e.Detected = "detected";
})(Ds ||= {}), X.Leak, Z.Sensor, Ds.Detected, Ds.Detected, Ds.Detected, Q.Binary, Ds.Detected, Ds.Detected;
//#endregion
//#region ../../sdk/node/dist/sensor/licensePlate.js
var Os;
(function(e) {
	e.Detected = "detected", e.Detections = "detections";
})(Os ||= {}), X.LicensePlate, Z.Sensor, Os.Detected, Os.Detections;
//#endregion
//#region ../../sdk/node/dist/sensor/light.js
var ks;
(function(e) {
	e.Brightness = "brightness";
})(ks ||= {});
var As;
(function(e) {
	e.On = "on", e.Brightness = "brightness";
})(As ||= {}), X.Light, Z.Control, As.On, As.Brightness, As.On, As.Brightness, ks.Brightness, As.On, As.Brightness, ks.Brightness, Q.Light, As.On, As.On;
//#endregion
//#region ../../sdk/node/dist/sensor/lock.js
var js;
(function(e) {
	e[e.Secured = 0] = "Secured", e[e.Unsecured = 1] = "Unsecured", e[e.Unknown = 2] = "Unknown";
})(js ||= {});
var Ms;
(function(e) {
	e.CurrentState = "currentState", e.TargetState = "targetState";
})(Ms ||= {}), X.Lock, Z.Control, Ms.CurrentState, js.Secured, js.Unsecured, js.Unknown, Ms.TargetState, js.Secured, js.Unsecured, Ms.CurrentState, Ms.CurrentState, Ms.TargetState, Q.Lock, Ms.CurrentState, Ms.TargetState, js.Secured, js.Unsecured;
//#endregion
//#region ../../sdk/node/dist/sensor/motion.js
var Ns;
(function(e) {
	e.Detected = "detected", e.Detections = "detections", e.Blocked = "blocked", e.LastTriggered = "lastTriggered";
})(Ns ||= {}), X.Motion, Z.Sensor, Ns.Detected, Ns.Detections, Ns.Blocked, Ns.LastTriggered;
//#endregion
//#region ../../sdk/node/dist/sensor/object.js
var Ps;
(function(e) {
	e.Detected = "detected", e.Detections = "detections", e.Labels = "labels";
})(Ps ||= {}), X.Object, Z.Sensor, Ps.Detected, Ps.Detections, Ps.Labels, X.ObjectAssist, Z.Sensor;
//#endregion
//#region ../../sdk/node/dist/sensor/occupancy.js
var Fs;
(function(e) {
	e.Detected = "detected";
})(Fs ||= {}), X.Occupancy, Z.Sensor, Fs.Detected, Fs.Detected, Fs.Detected, Q.Binary, Fs.Detected, Fs.Detected;
//#endregion
//#region ../../sdk/node/dist/sensor/power.js
var Is;
(function(e) {
	e.Detected = "detected";
})(Is ||= {}), X.Power, Z.Sensor, Is.Detected, Is.Detected, Is.Detected, Q.Binary, Is.Detected, Is.Detected;
//#endregion
//#region ../../sdk/node/dist/sensor/problem.js
var Ls;
(function(e) {
	e.Detected = "detected";
})(Ls ||= {}), X.Problem, Z.Sensor, Ls.Detected, Ls.Detected, Ls.Detected, Q.Binary, Ls.Detected, Ls.Detected;
//#endregion
//#region ../../sdk/node/dist/sensor/ptz.js
var Rs;
(function(e) {
	e.Pan = "pan", e.Tilt = "tilt", e.Zoom = "zoom", e.Presets = "presets", e.Home = "home", e.RelativeMove = "relativeMove", e.AbsolutePosition = "absolutePosition", e.VelocityControl = "velocityControl";
})(Rs ||= {});
var zs;
(function(e) {
	e.Position = "position", e.Moving = "moving", e.Presets = "presets", e.Velocity = "velocity", e.TargetPreset = "targetPreset", e.RelativeMove = "relativeMove", e.Home = "home";
})(zs ||= {}), X.PTZ, Z.Control, zs.Position, zs.Moving, zs.Presets, zs.Velocity, zs.TargetPreset, zs.RelativeMove, zs.Home;
//#endregion
//#region ../../sdk/node/dist/sensor/securitySystem.js
var Bs;
(function(e) {
	e[e.StayArm = 0] = "StayArm", e[e.AwayArm = 1] = "AwayArm", e[e.NightArm = 2] = "NightArm", e[e.Disarmed = 3] = "Disarmed", e[e.AlarmTriggered = 4] = "AlarmTriggered";
})(Bs ||= {});
var Vs;
(function(e) {
	e.CurrentState = "currentState", e.TargetState = "targetState";
})(Vs ||= {}), X.SecuritySystem, Z.Control, Vs.CurrentState, Bs.StayArm, Bs.AwayArm, Bs.NightArm, Bs.Disarmed, Bs.AlarmTriggered, Vs.TargetState, Bs.StayArm, Bs.AwayArm, Bs.NightArm, Bs.Disarmed, Vs.CurrentState, Vs.CurrentState, Vs.TargetState, Q.Alarm, Vs.CurrentState, Vs.TargetState, Bs.StayArm, Bs.AwayArm, Bs.NightArm, Bs.Disarmed, Bs.AlarmTriggered;
//#endregion
//#region ../../sdk/node/dist/sensor/siren.js
var Hs;
(function(e) {
	e.Volume = "volume";
})(Hs ||= {});
var Us;
(function(e) {
	e.Active = "active", e.Volume = "volume";
})(Us ||= {}), X.Siren, Z.Control, Us.Active, Us.Volume, Us.Active, Us.Volume, Hs.Volume, Us.Active, Us.Volume, Hs.Volume, Q.Siren, Us.Active, Us.Active;
//#endregion
//#region ../../sdk/node/dist/sensor/smoke.js
var Ws;
(function(e) {
	e.Detected = "detected";
})(Ws ||= {}), X.Smoke, Z.Sensor, Ws.Detected, Ws.Detected, Ws.Detected, Q.Binary, Ws.Detected, Ws.Detected;
//#endregion
//#region ../../sdk/node/dist/sensor/switch.js
var Gs;
(function(e) {
	e.On = "on";
})(Gs ||= {}), X.Switch, Z.Control, Gs.On, Gs.On, Gs.On, Q.Switch, Gs.On, Gs.On;
//#endregion
//#region ../../sdk/node/dist/sensor/tamper.js
var Ks;
(function(e) {
	e.Detected = "detected";
})(Ks ||= {}), X.Tamper, Z.Sensor, Ks.Detected, Ks.Detected, Ks.Detected, Q.Binary, Ks.Detected, Ks.Detected;
//#endregion
//#region ../../sdk/node/dist/sensor/temperature.js
var qs;
(function(e) {
	e.Current = "current";
})(qs ||= {}), X.Temperature, Z.Info, qs.Current, qs.Current, Q.Measurement, qs.Current, qs.Current;
//#endregion
//#region ../../sdk/node/dist/sensor/vibration.js
var Js;
(function(e) {
	e.Detected = "detected";
})(Js ||= {}), X.Vibration, Z.Sensor, Js.Detected, Js.Detected, Js.Detected, Q.Binary, Js.Detected, Js.Detected;
//#endregion
//#region node_modules/@camera.ui/browser/dist/index.js
function Ys(e = {}) {
	let { releaseDelay: t = 1e3, onRelease: n } = e, r = /* @__PURE__ */ new Map(), i = /* @__PURE__ */ new Map();
	function a(e) {
		let t = i.get(e);
		t && (clearTimeout(t), i.delete(e));
	}
	function o(e) {
		let t = r.get(e);
		if (t) {
			try {
				n?.(e, t.value);
			} catch {}
			r.delete(e);
		}
		i.delete(e);
	}
	function s(e, t) {
		a(e);
		let n = r.get(e);
		if (n) return n.refCount++, n.value;
		let i = t();
		return r.set(e, {
			value: i,
			refCount: 1
		}), i;
	}
	function c(e) {
		let n = r.get(e);
		if (n && (n.refCount--, n.refCount <= 0)) {
			let n = setTimeout(() => {
				let t = r.get(e);
				t && t.refCount <= 0 ? o(e) : i.delete(e);
			}, t);
			i.set(e, n);
		}
	}
	function l(e) {
		return r.get(e)?.value;
	}
	function u(e) {
		return r.has(e);
	}
	function d(e) {
		a(e), o(e);
	}
	function f() {
		for (let e of i.keys()) a(e);
		for (let e of r.keys()) o(e);
	}
	function p(e) {
		return r.get(e)?.refCount ?? 0;
	}
	function m(e) {
		for (let [t, n] of r) e(n.value, t);
	}
	return {
		acquire: s,
		release: c,
		get: l,
		has: u,
		forceRelease: d,
		clear: f,
		getRefCount: p,
		forEachValue: m
	};
}
function Xs() {
	let e = er(jc);
	if (!e) throw Error("[camera.ui] useCameraUi() called without CameraUiPlugin installed. Make sure to call app.use(createCameraUiPlugin({ ... })) before using this composable.");
	return e;
}
function Zs(e) {
	return e.replace(/ /g, "_").toLowerCase();
}
function Qs(e, t) {
	return `cui_${Zs(e)}_${Zs(t)}`;
}
var $s = class {
	static coreManagerNamespaces() {
		return {
			coreManagerSubject: "coreManager.subscriber",
			coreManagerRpc: "coreManager.rpc"
		};
	}
	static deviceManagerNamespaces() {
		return {
			deviceManagerSubject: "deviceManager.subscriber",
			deviceManagerRpc: "deviceManager.rpc"
		};
	}
	static discoveryManagerNamespaces() {
		return {
			discoveryManagerSubject: "discoveryManager.subscriber",
			discoveryManagerRpc: "discoveryManager.rpc"
		};
	}
	static pluginNamespaces(e) {
		return {
			pluginDeviceManagerSubject: `plugin.${e}.deviceManager.subscriber`,
			pluginChildRpc: `plugin.${e}.child.rpc`,
			pluginChild: `plugin.${e}.child`,
			pluginStorageRpc: `plugin.${e}.storage.rpc`,
			pluginConfigStoreRpc: `plugin.${e}.configstore.rpc`
		};
	}
	static pluginFileServeRpc(e) {
		return `plugin.${e}.fileserve.rpc`;
	}
	static cameraNamespaces(e) {
		return {
			cameraSubject: `camera.${e}.subscriber`,
			cameraControllerRpc: `camera.${e}.controller.rpc`
		};
	}
	static frameWorkerNamespaces(e) {
		return {
			frameWorkerChildRpc: `camera.${e}.frameWorker.child.rpc`,
			frameWorkerChild: `camera.${e}.frameWorker.child`
		};
	}
	static pluginCameraNamespaces(e, t) {
		return {
			cameraInterfacesRpc: `plugin.${e}.camera.${t}.cameraInterfaces.rpc`,
			cameraStorageRpc: `plugin.${e}.camera.${t}.cameraStorage.rpc`,
			cameraImplRpc: `plugin.${e}.camera.${t}.impl.rpc`
		};
	}
	static pluginSensorNamespaces(e, t) {
		return { sensorStorageRpc: `plugin.${e}.sensor.${t}.storage.rpc` };
	}
	static sensorRegistryNamespaces() {
		return {
			sensorsSubject: "sensors.subject",
			sensorsRpc: "sensors.rpc"
		};
	}
	static sensorCameraViewNamespaces(e) {
		return { sensorWriteSubject: `camera.${e}.sensors.writes` };
	}
	static sensorEventNamespaces(e) {
		return { sensorSubject: `sensor.${e}.subject` };
	}
	static sensorProviderNamespaces(e, t) {
		return { sensorRpc: `plugin.${e}.sensor.${t}.rpc` };
	}
	static legacySensorNamespaces(e) {
		return {
			sensorSubject: `camera.${e}.sensors.subject`,
			sensorRpc: `camera.${e}.sensors.rpc`
		};
	}
	static frameWorkerDetectionNamespaces(e) {
		return { detectionRpc: `camera.${e}.frameWorker.detection.rpc` };
	}
	static detectionEventNamespaces(e) {
		return { detectionEventSubject: `camera.${e}.events.subject` };
	}
	static terminalManagerNamespaces() {
		return {
			terminalManagerSubject: "terminalManager.subscriber",
			terminalManagerRpc: "terminalManager.rpc"
		};
	}
	static downloadManagerNamespaces() {
		return { downloadManagerRpc: "downloadManager.rpc" };
	}
	static notificationManagerNamespaces() {
		return { notificationsPublishSubject: "notifications.publish" };
	}
	static workerAgentRpc(e) {
		return `worker.${e}.rpc`;
	}
	static workerManagerRpc() {
		return "workers.manager.rpc";
	}
	static workerSync(e) {
		return `worker.${e}.sync`;
	}
	static workerDisconnect() {
		return "workers.disconnect";
	}
	static workerLogs() {
		return "workers.logs";
	}
}, ec = 3, tc = 3e4;
async function nc(e, t, n = {}) {
	let r = n.maxRetries ?? ec, i = n.awaitConnect ?? !0, a = n.connectTimeoutMs ?? tc, o = n.retryDelayMs ?? rc, s = n.shouldRetry ?? ic, c = n.signal, l;
	for (let n = 0; n <= r; n++) {
		if (c?.aborted) throw sc();
		let u = e.value;
		if (!u) {
			if (!i) throw Error("rpc: not connected");
			u = await ac(e, a, c);
		}
		try {
			return await t(u);
		} catch (e) {
			if (l = e, n >= r || !s(e, n)) throw e;
			await oc(o(n), c);
		}
	}
	throw l ?? /* @__PURE__ */ Error("rpc: max retries exceeded");
}
function rc(e) {
	return Math.min(100 * 2 ** e, 1e3);
}
function ic(e) {
	if (!(e instanceof Error)) return !1;
	let t = e.code;
	if (t === "TIMEOUT" || t === "CONNECTION_CLOSED") return !0;
	let n = e.message.toLowerCase();
	return !!(n.includes("not connected") || n.includes("connection closed") || n.includes("no responders") || n.includes("connection refused") || n.includes("socket") || n.includes("timed out") || n.includes("timeout"));
}
async function ac(e, t, n) {
	return e.value ? e.value : new Promise((r, i) => {
		let a = setTimeout(() => {
			s(), n?.removeEventListener("abort", o), i(/* @__PURE__ */ Error("rpc: connect timeout"));
		}, t), o = () => {
			clearTimeout(a), s(), i(sc());
		};
		n?.addEventListener("abort", o, { once: !0 });
		let s = G(e, (e) => {
			e && (clearTimeout(a), s(), n?.removeEventListener("abort", o), r(e));
		});
	});
}
async function oc(e, t) {
	return new Promise((n, r) => {
		if (t?.aborted) {
			r(sc());
			return;
		}
		let i = setTimeout(() => {
			t?.removeEventListener("abort", a), n();
		}, e), a = () => {
			clearTimeout(i), r(sc());
		};
		t?.addEventListener("abort", a, { once: !0 });
	});
}
function sc() {
	if (typeof DOMException < "u") return new DOMException("Aborted", "AbortError");
	let e = /* @__PURE__ */ Error("Aborted");
	return e.name = "AbortError", e;
}
var cc = 5e3, lc = /* @__PURE__ */ new Map(), uc = /* @__PURE__ */ new Map(), dc = /* @__PURE__ */ new Map(), fc = /* @__PURE__ */ new Map();
function pc(e) {
	fc.get(e)?.forEach((e) => e());
}
function mc(e) {
	setTimeout(() => URL.revokeObjectURL(e), cc);
}
function hc(e, t, n) {
	let r = dc.get(e);
	r && (mc(r), dc.delete(e)), lc.set(e, t), n !== void 0 && uc.set(e, n), pc(e);
}
function gc(e) {
	return lc.get(e);
}
function _c(e, t) {
	return fc.has(e) || fc.set(e, /* @__PURE__ */ new Set()), fc.get(e).add(t), () => {
		fc.get(e)?.delete(t);
	};
}
async function vc(e, t) {
	let n = $s.cameraNamespaces(t._id), r = $s.sensorRegistryNamespaces(), i = "rpc" in e && "value" in e.rpc ? e : void 0, a = i ? i.rpc : /* @__PURE__ */ H(e), o, s, c = /* @__PURE__ */ H(t), l = /* @__PURE__ */ V(!1), u = /* @__PURE__ */ V(!1), d = /* @__PURE__ */ H(gc(t._id)), f = /* @__PURE__ */ V(!1), p = /* @__PURE__ */ V({}), m = _c(t._id, () => {
		d.value = gc(t._id);
	}), h = Y(() => c.value.name), g = Y(() => c.value.room), _ = Y(() => c.value.nativeId), v = Y(() => c.value.disabled), y = Y(() => c.value.detectionSettings?.snooze ?? !1), b = Y(() => c.value.isCloud), x = Y(() => JSON.parse(JSON.stringify(c.value.sources)).map((e) => ({
		...e,
		snapshot: async (t) => M(e._id, t),
		probeStream: async (t, n = !1) => ae(e._id, t, n)
	}))), S = Y(() => x.value.find((e) => e.role === "high-resolution")), ee = Y(() => x.value.find((e) => e.role === "mid-resolution")), C = Y(() => x.value.find((e) => e.role === "low-resolution")), w = Y(() => S.value ?? ee.value ?? C.value), T = Y(() => x.value.find((e) => e.role === "snapshot") ?? x.value.find((e) => e.useForSnapshot)), E = Y(() => {
		let e = /* @__PURE__ */ new Set();
		for (let t of Object.values(p.value)) e.add(t.type);
		return e;
	}), te = Y(() => Array.from(E.value)), D = Y(() => E.value.has(X.Light)), ne = Y(() => E.value.has(X.Siren)), O = Y(() => E.value.has(X.Doorbell)), k = Y(() => E.value.has(X.Battery)), A = Y(() => E.value.has(X.Audio)), re = Y(() => E.value.has(X.Motion)), ie = Y(() => E.value.has(X.Object)), j = Y(() => E.value.has(X.PTZ));
	async function M(e, r) {
		f.value = !0;
		try {
			try {
				let i = await nc(a, (t) => t.createProxy(n.cameraControllerRpc).snapshotWithMeta(e, r));
				return i && i.data.byteLength > 0 ? (hc(t._id, i.data, Date.now() - i.ageMs), i.data) : void 0;
			} catch {
				let i = await nc(a, (t) => t.createProxy(n.cameraControllerRpc).snapshot(e, r));
				if (i && i.byteLength > 0) return hc(t._id, i, r ? Date.now() : void 0), i;
			}
		} finally {
			f.value = !1;
		}
	}
	async function ae(e, t, r = !1) {
		return nc(a, (i) => i.createProxy(n.cameraControllerRpc).probeStream(e, t, r));
	}
	async function oe(e) {
		return nc(a, (t) => t.createProxy(n.cameraControllerRpc).streamUrl(e));
	}
	async function se() {
		let e = await nc(a, (e) => e.createProxy(n.cameraControllerRpc).refreshStates());
		c.value = e.camera, l.value = e.cameraState, u.value = e.frameWorkerState, p.value = e.sensorStates;
	}
	async function N(e) {
		switch (e.type) {
			case "removed":
				await F();
				break;
			case "updated":
				c.value = e.data;
				break;
			case "cameraState":
				l.value = e.data;
				break;
			case "frameWorkerState":
				u.value = e.data;
				break;
			case "snapshot:updated": hc(t._id, e.data.snapshot, Date.now());
		}
	}
	function P(e) {
		if (e.type === "sensor:added") {
			let n = e.data;
			if (!n.sensor.assignedCameraIds.includes(t._id) || !n.sensor.connected) return;
			p.value = {
				...p.value,
				[n.sensor.id]: n.state
			};
		} else if (e.type === "sensor:deleted") {
			let t = e.data, n = { ...p.value };
			delete n[t.sensorId], p.value = n;
		} else if (e.type === "sensor:connected:changed") {
			let t = e.data;
			if (t.connected) se().catch(() => {});
			else {
				let e = { ...p.value };
				delete e[t.sensorId], p.value = e;
			}
		} else if (e.type === "sensor:assignment:changed") {
			let n = e.data;
			if (n.cameraId !== t._id) return;
			if (n.assigned) se().catch(() => {});
			else {
				let e = { ...p.value };
				delete e[n.sensorId], p.value = e;
			}
		}
	}
	async function ce() {
		o?.(), s?.(), o = await nc(a, (e) => e.subscribe(n.cameraSubject, N)), s = await nc(a, (e) => e.subscribe(r.sensorsSubject, P)), await se();
	}
	async function F() {
		o?.(), o = void 0, s?.(), s = void 0, m();
	}
	async function le(e, t) {
		let n = x.value.find((e) => e.useForSnapshot), r = x.value.find((e) => e.role === "snapshot"), i = e ?? r?._id ?? n?._id ?? C.value?._id ?? ee.value?._id ?? S.value?._id ?? w.value?._id;
		return i ? M(i, t) : Promise.resolve(void 0);
	}
	async function ue(e, t, n = !1) {
		let r = e ?? w.value?._id;
		return r ? ae(r, t, n) : Promise.resolve(void 0);
	}
	return await ce(), {
		id: t._id,
		name: h,
		room: g,
		nativeId: _,
		disabled: v,
		snooze: y,
		isCloud: b,
		connected: l,
		frameWorkerConnected: u,
		sources: x,
		streamSource: w,
		snapshotSource: T,
		highResolutionSource: S,
		midResolutionSource: ee,
		lowResolutionSource: C,
		capabilities: te,
		hasLight: D,
		hasSiren: ne,
		hasDoorbell: O,
		hasBattery: k,
		hasAudioSensor: A,
		hasMotionSensor: re,
		hasObjectSensor: ie,
		hasPtz: j,
		camera: c,
		snapshot: d,
		snapshotLoading: f,
		fetchSnapshot: le,
		probeStream: ue,
		streamUrl: oe,
		refreshStates: se,
		reconnect: ce,
		close: F
	};
}
function yc() {
	let e = Xs(), t = $s.deviceManagerNamespaces();
	async function n(n) {
		let r = await nc(e.rpc, (e) => e.createProxy(t.deviceManagerRpc).getCamera(n, "@camera.ui/browser"));
		if (r) return vc(e, r);
	}
	return { getCamera: n };
}
var bc = Ys({
	releaseDelay: 1e3,
	onRelease: (e, t) => t.close()
}), xc = /* @__PURE__ */ new Map();
function Sc() {
	bc.forEachValue((e) => {
		e.reconnect().catch(() => {});
	});
}
function Cc(e) {
	let { isConnected: t } = Xs(), n = yc(), r = /* @__PURE__ */ H(), i = /* @__PURE__ */ V(!1), a = /* @__PURE__ */ V(!1), o = /* @__PURE__ */ V(), s;
	async function c(c) {
		if (!t.value || !c) return;
		if (s && s !== c && (bc.release(s), r.value = void 0, s = void 0), bc.has(c)) {
			let e = bc.acquire(c, () => {
				throw Error("Should not create - already cached");
			});
			s = c, r.value = e, a.value = !0;
			return;
		}
		let l = xc.get(c);
		if (l) {
			i.value = !0;
			try {
				let t = await l;
				if (t && bc.has(c) && W(e) === c) {
					let e = bc.acquire(c, () => t);
					s = c, r.value = e;
				}
			} catch (e) {
				o.value = e instanceof Error ? e : Error(String(e));
			} finally {
				i.value = !1, a.value = !0;
			}
			return;
		}
		i.value = !0, o.value = void 0;
		let u = n.getCamera(c);
		xc.set(c, u);
		try {
			let t = await u;
			if (t) {
				if (bc.acquire(c, () => t), W(e) !== c) {
					bc.release(c);
					return;
				}
				s = c, r.value = t;
			}
		} catch (e) {
			o.value = e instanceof Error ? e : Error(String(e));
		} finally {
			xc.delete(c), i.value = !1, a.value = !0;
		}
	}
	async function l() {
		let t = W(e);
		t && (s &&= (bc.getRefCount(s) <= 1 ? bc.forceRelease(s) : bc.release(s), r.value = void 0, void 0), await c(t));
	}
	return G([t, () => W(e)], async ([e, t]) => {
		e && t ? await c(t) : !e && s && (bc.release(s), r.value = void 0, s = void 0);
	}, { immediate: !0 }), Lo(() => {
		s &&= (bc.release(s), r.value = void 0, void 0);
	}), {
		camera: r,
		isLoading: Y(() => i.value || !a.value),
		error: o,
		refresh: l
	};
}
var wc = Ys({ releaseDelay: 1e3 }), Tc = /* @__PURE__ */ new Map(), Ec = /* @__PURE__ */ new Set();
function Dc() {
	wc.clear(), Tc.clear();
	for (let e of Ec) try {
		e();
	} catch {}
}
X.Light, X.Siren, X.Battery, X.Doorbell, X.Contact, X.Motion, X.Object, X.Audio, X.Face, X.LicensePlate, X.Classifier, X.PTZ, X.Switch, X.Lock, X.SecuritySystem, X.Temperature, X.Humidity, X.Occupancy, X.Smoke, X.Leak, X.Garage;
var Oc = Ys({
	releaseDelay: 1e3,
	onRelease: (e, t) => t.manager.close()
});
function kc() {
	Oc.forEachValue((e) => {
		e.initPromise = e.manager.reconnect();
	});
}
Ys({ releaseDelay: 1e3 });
function Ac() {
	Dc(), Sc(), kc();
}
var jc = Symbol("camera-ui"), Mc = new w("plugin");
function Nc(e) {
	return "rpc" in e && "isConnected" in e;
}
var Pc = 4e3;
function Fc(e) {
	let { natsTransport: t, target: n, wsTransport: r } = e, i = t.getClient() !== null, a = t.getClient(), o = null, s = /* @__PURE__ */ H(t.getClient() ?? void 0), c = /* @__PURE__ */ V(t.getClient()?.isConnected ?? !1), l = /* @__PURE__ */ V(void 0), u = Y(() => n.value?.endpoint.url), d = Y(() => n.value?.tokens.access), f = Y(() => {
		let e = n.value;
		if (e?.tokens.proxySession) return { session: e.tokens.proxySession };
	}), p = /* @__PURE__ */ new Map();
	function m(e, t) {
		let n = p.get(e);
		n || (n = /* @__PURE__ */ new Set(), p.set(e, n)), n.add(t);
	}
	function h(e, t) {
		p.get(e)?.delete(t);
	}
	function g(e) {
		let t = p.get(e);
		if (t) for (let e of t) try {
			e();
		} catch (e) {
			Mc.warn("context listener threw:", e);
		}
	}
	return t.subscribeClient((e) => {
		if (e) {
			o !== null && (clearTimeout(o), o = null);
			let t = c.value, n = e !== a;
			a = e, s.value = e, c.value = !0, l.value = void 0, (!t || n) && (Ac(), i && g("reconnected"), i = !0);
		} else {
			if (s.value = void 0, o !== null || !c.value) return;
			o = setTimeout(() => {
				o = null, c.value = !1, g("disconnected");
			}, Pc);
		}
	}), t.on("auth-error", (e) => {
		l.value = Error(e.message ?? "auth-error");
	}), t.on("down", (e) => {
		l.value ||= Error(e.reason);
	}), t.on("up", () => {
		l.value = void 0;
	}), fn({
		rpc: s,
		target: /* @__PURE__ */ an(n),
		isConnected: /* @__PURE__ */ an(c),
		endpoint: u,
		token: d,
		extraProxyQuery: f,
		error: /* @__PURE__ */ an(l),
		wsTransport: r,
		on: m,
		off: h
	});
}
function Ic(e) {
	return { install(t) {
		let n = Nc(e) ? e : Fc(e);
		t.provide(jc, n);
	} };
}
var Lc = {
	standbyTimeout: 5e3,
	activityTimeout: 5e3
};
function Rc(e) {
	let { initialMode: t = "always-on", config: n = {}, onStreamStart: r, onStreamStop: i, isStreamPlaying: a } = e, o = {
		...Lc,
		...n
	}, s = /* @__PURE__ */ V(t), c = /* @__PURE__ */ V(!1), l = /* @__PURE__ */ V(!1), u, d;
	function f() {
		u &&= (clearTimeout(u), void 0);
	}
	function p() {
		d &&= (clearTimeout(d), void 0);
	}
	function m() {
		f(), p();
	}
	function h() {
		c.value || (c.value = !0, i());
	}
	function g() {
		c.value && (c.value = !1, r());
	}
	function _() {
		switch (m(), s.value) {
			case "always-on":
				c.value = !1, a() || r();
				break;
			case "standby":
				c.value || (a() || r(), v());
				break;
			case "activity": l.value ? (c.value = !1, a() || r()) : u = setTimeout(() => {
				s.value === "activity" && !l.value && h();
			}, o.activityTimeout);
		}
	}
	function v() {
		p(), d = setTimeout(() => {
			s.value === "standby" && h();
		}, o.standbyTimeout);
	}
	function y(e) {
		s.value !== e && (s.value = e, _());
	}
	function b(e) {
		s.value === "activity" && (e ? (l.value = !0, f(), (c.value || !a()) && g()) : (l.value = !1, f(), u = setTimeout(() => {
			l.value || h();
		}, o.activityTimeout)));
	}
	function x() {
		if (c.value) switch (g(), s.value) {
			case "standby":
				v();
				break;
			case "activity": f(), l.value || (u = setTimeout(() => {
				h();
			}, o.activityTimeout));
		}
	}
	function S() {
		s.value === "standby" && !c.value && v();
	}
	function ee() {
		m();
	}
	return {
		mode: s,
		inStandby: c,
		hasActivity: l,
		setMode: y,
		reportActivity: b,
		resumeFromStandby: x,
		resetIdleTimer: S,
		dispose: ee
	};
}
var zc = 3e4, Bc = new w("TabVisibility"), Vc = /* @__PURE__ */ V(typeof document > "u" || document.visibilityState === "visible"), Hc = null, Uc = /* @__PURE__ */ new Set(), Wc = /* @__PURE__ */ new Set(), Gc = /* @__PURE__ */ new Set(), Kc = !1;
function qc(e) {
	Bc.debug(`paused listener fired (delay ${e.delayMs}ms reached)`);
	try {
		e.cb();
	} catch (e) {
		Bc.error("onTabPaused listener threw:", e);
	}
}
function Jc(e) {
	Bc.debug(`paused listener scheduled in ${e.delayMs}ms`), e.timer = setTimeout(() => {
		if (e.timer = null, Vc.value) {
			Bc.debug("paused listener skipped — tab visible before delay");
			return;
		}
		qc(e);
	}, e.delayMs);
}
function Yc() {
	for (let e of Wc) e.timer !== null && (clearTimeout(e.timer), e.timer = null);
}
function Xc() {
	Kc || typeof document > "u" || (Kc = !0, document.addEventListener("visibilitychange", () => {
		let e = document.visibilityState === "visible";
		if (!e && Vc.value) {
			Vc.value = !1, Hc = Date.now(), Bc.debug(`tab → hidden (hidden=${Uc.size} paused=${Wc.size})`);
			for (let e of Uc) try {
				e.cb();
			} catch (e) {
				Bc.error("onTabHidden listener threw:", e);
			}
			for (let e of Wc) Jc(e);
		} else if (e && !Vc.value) {
			Yc();
			let e = Hc == null ? 0 : Date.now() - Hc;
			Hc = null, Vc.value = !0, Bc.debug(`tab → visible (hiddenMs=${e}, visible-listeners=${Gc.size})`);
			for (let { cb: t } of Gc) try {
				t({ hiddenMs: e });
			} catch (e) {
				Bc.error("onTabVisible listener threw:", e);
			}
		}
	}));
}
function Zc() {
	Xc();
	let e = Y(() => Vc.value);
	function t(e) {
		let t = { cb: e };
		Uc.add(t);
		let n = () => {
			Uc.delete(t);
		};
		return Lo(n), n;
	}
	function n(e, t = {}) {
		let n = {
			cb: e,
			delayMs: t.delayMs ?? zc,
			timer: null
		};
		Wc.add(n);
		let r = () => {
			n.timer !== null && (clearTimeout(n.timer), n.timer = null), Wc.delete(n);
		};
		return Lo(r), r;
	}
	function r(e) {
		let t = { cb: e };
		Gc.add(t);
		let n = () => {
			Gc.delete(t);
		};
		return Lo(n), n;
	}
	return {
		isVisible: e,
		onTabHidden: t,
		onTabPaused: n,
		onTabVisible: r
	};
}
var Qc = {
	WEBRTC: {
		RECONNECT_DELAY: 1e3,
		CONNECT_TIMEOUT: 1e4,
		WS_CONNECT_TIMEOUT: 5e3,
		ICE_SERVERS: [{ urls: "stun:stun.l.google.com:19302" }]
	},
	MSE: {
		BUFFER_SIZE: 2097152,
		BUFFER_WINDOW: 5
	},
	CODECS: {
		DEFAULT: [
			"avc1.640029",
			"avc1.64002A",
			"avc1.640033",
			"hvc1.1.6.L153.B0",
			"mp4a.40.2",
			"mp4a.40.5",
			"flac",
			"opus"
		],
		WEBRTC_VIDEO: [
			"H264",
			"VP8",
			"VP9"
		],
		WEBRTC_AUDIO: [
			"opus",
			"G722",
			"PCMU",
			"PCMA"
		]
	}
}, $c = "hvc1.1.6.L153.B0";
function el() {
	return navigator.userAgent.match(/version\/(\d+)/i);
}
function tl() {
	let e = [...Qc.CODECS.DEFAULT], t = el();
	if (t?.[1]) {
		let n = parseInt(t[1], 10);
		if (n < 13) {
			let t = e.indexOf("mp4a.40.2");
			t > -1 && e.splice(t);
		} else if (n < 14) {
			let t = e.indexOf("flac");
			t > -1 && e.splice(t);
		} else {
			let t = e.indexOf("opus");
			t > -1 && e.splice(t);
		}
	}
	return e;
}
function nl(e, t) {
	return e.filter((e) => t(`video/mp4; codecs="${e}"`)).join(",");
}
function rl(e) {
	return Qc.CODECS.WEBRTC_AUDIO.includes(e);
}
function il(e) {
	return Qc.CODECS.WEBRTC_VIDEO.includes(e) ? !0 : e === "H265" && ll();
}
var al, ol;
function sl(e) {
	if (e === "auto") return sl("webrtc") || sl("mse");
	if (e === "mse") return al === void 0 && (al = !!fl()?.isTypeSupported(`video/mp4; codecs="${$c}"`)), al;
	if (ol === void 0) try {
		ol = !!(RTCRtpReceiver?.getCapabilities("video")?.codecs)?.some((e) => e.mimeType.toLowerCase().includes("h265") || e.mimeType.toLowerCase().includes("hevc"));
	} catch {
		ol = !1;
	}
	return ol;
}
function cl(e) {
	e === "mse" ? al = !1 : ol = !1;
}
function ll() {
	return sl("webrtc");
}
function ul(e) {
	let t = e.audio.filter((e) => e.direction === "sendonly"), n = e.video.filter((e) => e.direction === "sendonly"), r = t.length === 0 || t.some((e) => rl(e.codec)), i = n.length === 0 || n.some((e) => il(e.codec)), a = [];
	return r || a.push(...t.map((e) => e.codec)), i || a.push(...n.map((e) => e.codec)), {
		compatible: r && i,
		audioCompatible: r,
		videoCompatible: i,
		incompatibleCodecs: a
	};
}
function dl() {
	return "ManagedMediaSource" in window;
}
function fl() {
	if (dl()) return window.ManagedMediaSource;
	if ("MediaSource" in window) return window.MediaSource;
}
function pl(e, t) {
	return new Promise((n, r) => {
		if (t.aborted) {
			r(new DOMException("Aborted", "AbortError"));
			return;
		}
		let i = setTimeout(n, e);
		t.addEventListener("abort", () => {
			clearTimeout(i), r(new DOMException("Aborted", "AbortError"));
		}, { once: !0 });
	});
}
function ml(e) {
	let { videoElement: t, onReady: n, onFirstData: r, onError: i, signal: a } = e, o = null, s = null, c = null, l = !1, u = !1, d = new Uint8Array(Qc.MSE.BUFFER_SIZE), f = 0, p = [], m = tl();
	function h() {
		if (a.aborted) return;
		let e = fl();
		if (!e) {
			i(/* @__PURE__ */ Error("MediaSource not supported"));
			return;
		}
		o = new e();
		let n = dl(), r = t.src;
		return o.addEventListener("sourceopen", () => {
			a.aborted || !n && r && r.startsWith("blob:") && r !== t.src && URL.revokeObjectURL(r);
		}, { once: !0 }), n ? (t.disableRemotePlayback = !0, t.srcObject = o) : (c = URL.createObjectURL(o), t.src = c, t.srcObject = null), nl(m, e.isTypeSupported.bind(e));
	}
	function g(e) {
		if (a.aborted || !o) return;
		if (o.readyState !== "open") {
			o.addEventListener("sourceopen", () => {
				a.aborted || g(e);
			}, { once: !0 });
			return;
		}
		f = 0, d = new Uint8Array(Qc.MSE.BUFFER_SIZE);
		let t = fl();
		if (t && !t.isTypeSupported(e)) {
			i(/* @__PURE__ */ Error(`MIME type not supported: ${e}`));
			return;
		}
		try {
			if (s = o.addSourceBuffer(e), s.mode = "segments", s.addEventListener("updateend", _), l = !0, p.length > 0) {
				for (let e of p) v(e);
				p.length = 0;
			}
			n();
		} catch (e) {
			i(e instanceof Error ? e : Error(String(e)));
		}
	}
	function _() {
		if (!(a.aborted || !s || !o)) {
			if (!s.updating && f > 0) try {
				let e = d.slice(0, f);
				s.appendBuffer(e), f = 0;
			} catch (e) {
				y(e) || i(e instanceof Error ? e : Error(String(e)));
			}
			if (!s.updating && s.buffered?.length) {
				let e = s.buffered.end(s.buffered.length - 1), n = e - Qc.MSE.BUFFER_WINDOW, i = s.buffered.start(0);
				if (u || (u = !0, r()), n > i) try {
					s.remove(i, n), o.setLiveSeekableRange(n, e);
				} catch {}
				t.currentTime < n && (t.currentTime = n);
				let a = e - t.currentTime;
				a > 1 ? t.playbackRate = 1.1 : a < .1 ? t.playbackRate = .9 : t.playbackRate = 1;
			}
		}
	}
	function v(e) {
		if (!a.aborted) {
			if (!s) {
				p.push(e);
				return;
			}
			if (o?.readyState === "closed") {
				i(/* @__PURE__ */ Error("MediaSource closed"));
				return;
			}
			if (s.updating || f > 0) {
				let t = new Uint8Array(e);
				if (f + t.byteLength > d.byteLength) {
					f = 0, i(/* @__PURE__ */ Error("MSE pending buffer overflow"));
					return;
				}
				d.set(t, f), f += t.byteLength;
			} else try {
				s.appendBuffer(e);
			} catch (t) {
				if (y(t)) {
					let t = new Uint8Array(e);
					t.byteLength <= d.byteLength && (d.set(t, 0), f = t.byteLength);
				}
			}
		}
	}
	function y(e) {
		if (e?.name !== "QuotaExceededError" || !s || s.updating || !s.buffered?.length) return !1;
		try {
			let e = s.buffered.start(0), t = s.buffered.end(s.buffered.length - 1), n = Math.max(e + 1, t - Qc.MSE.BUFFER_WINDOW);
			return n <= e ? !1 : (s.remove(e, n), !0);
		} catch {
			return !1;
		}
	}
	function b() {
		if (s) {
			if (s.removeEventListener("updateend", _), o?.readyState === "open") try {
				o.removeSourceBuffer(s);
			} catch {}
			s = null;
		}
		if (o?.readyState === "open") try {
			o.endOfStream();
		} catch {}
		o = null, c &&= (URL.revokeObjectURL(c), null), l = !1, u = !1, f = 0, p.length = 0;
	}
	return a.addEventListener("abort", b, { once: !0 }), {
		get mediaSource() {
			return o;
		},
		get sourceBuffer() {
			return s;
		},
		get isReady() {
			return l;
		},
		setup: h,
		initializeBuffer: g,
		appendBuffer: v,
		close: b
	};
}
async function hl(e) {
	try {
		await e.play();
	} catch {
		e.muted || (e.muted = !0, await hl(e));
	}
}
function gl(e, t, n) {
	let r = new RTCPeerConnection({
		bundlePolicy: "max-bundle",
		iceServers: [...Qc.WEBRTC.ICE_SERVERS]
	});
	return r.onicecandidate = (r) => {
		if (e.aborted || n && r.candidate?.protocol === "udp") return;
		let i = r.candidate?.toJSON().candidate ?? "";
		i && t(i);
	}, r;
}
async function _l(e, t, n) {
	t.aborted || !e || await e.setRemoteDescription({
		type: "answer",
		sdp: n
	});
}
async function vl(e, t, n, r) {
	t.aborted || !e || r && n.includes(" udp ") || await e.addIceCandidate({
		candidate: n,
		sdpMid: "0"
	});
}
async function yl(e, t, n) {
	if (!(t.aborted || !e)) try {
		await e.sender.replaceTrack(n);
	} catch {}
}
function bl(e) {
	e.micTransceiver &&= (e.micTransceiver.sender.replaceTrack(null).catch(() => {}), null), e.pc &&= (e.pc.getTransceivers().forEach((e) => e.sender?.track?.stop()), e.pc.close(), null), e.isConnected = !1;
}
function xl(e) {
	let { mode: t, onConnected: n, onDisconnected: r, onFailed: i, onCandidate: a, signal: o } = e, s = {
		pc: null,
		micTransceiver: null,
		isConnected: !1
	}, c = t === "webrtc/tcp";
	function l() {
		let e = gl(o, a, c);
		return e.onconnectionstatechange = () => {
			if (o.aborted) return;
			let t = e.connectionState;
			if (t === "connected") {
				s.isConnected = !0;
				let t = new MediaStream(e.getTransceivers().filter((e) => e.currentDirection === "recvonly").map((e) => e.receiver.track));
				n(t);
			} else t === "failed" ? (s.isConnected = !1, i()) : t === "disconnected" && (s.isConnected = !1, r());
		}, e.addTransceiver("video", { direction: "recvonly" }), e.addTransceiver("audio", { direction: "recvonly" }), s.micTransceiver = e.addTransceiver("audio", { direction: "sendonly" }), e;
	}
	async function u() {
		if (o.aborted) return;
		s.pc = l();
		let e = await s.pc.createOffer();
		return await s.pc.setLocalDescription(e), e.sdp;
	}
	function d() {
		bl(s);
	}
	return o.addEventListener("abort", d, { once: !0 }), {
		get pc() {
			return s.pc;
		},
		get micTransceiver() {
			return s.micTransceiver;
		},
		get isConnected() {
			return s.isConnected;
		},
		createOffer: u,
		handleAnswer: (e) => _l(s.pc, o, e),
		handleCandidate: (e) => vl(s.pc, o, e, c),
		setMicrophoneTrack: (e) => yl(s.micTransceiver, o, e),
		close: d
	};
}
function Sl(e) {
	let { onConnected: t, onDisconnected: n, onCandidate: r, signal: i } = e, a = {
		pc: null,
		micTransceiver: null,
		isConnected: !1
	};
	function o() {
		let e = gl(i, r, !1);
		return e.onconnectionstatechange = () => {
			if (i.aborted) return;
			let r = e.connectionState;
			r === "connected" ? (a.isConnected = !0, t()) : (r === "disconnected" || r === "failed") && (a.isConnected = !1, n());
		}, a.micTransceiver = e.addTransceiver("audio", { direction: "sendonly" }), e;
	}
	async function s() {
		if (i.aborted) return;
		a.pc = o();
		let e = await a.pc.createOffer();
		return await a.pc.setLocalDescription(e), e.sdp;
	}
	function c() {
		bl(a);
	}
	return i.addEventListener("abort", c, { once: !0 }), {
		get isConnected() {
			return a.isConnected;
		},
		createOffer: s,
		handleAnswer: (e) => _l(a.pc, i, e),
		handleCandidate: (e) => vl(a.pc, i, e, !1),
		setMicrophoneTrack: (e) => yl(a.micTransceiver, i, e),
		close: c
	};
}
async function Cl(e, t) {
	switch (t.type) {
		case "webrtc/answer":
			await e.handleAnswer(t.value);
			break;
		case "webrtc/candidate": t.value && await e.handleCandidate(t.value);
	}
}
var $ = new w("StreamConnection"), wl = class {
	status;
	activeMode;
	requestedMode;
	activeResolution;
	requestedResolution;
	degradedFrom;
	degradeReason;
	source;
	hasVideo;
	hasAudio;
	hasBackchannel;
	isPlaying;
	error;
	probeInfo;
	muted;
	paused;
	nativeWidth;
	nativeHeight;
	camera;
	videoElement;
	containerElement;
	target;
	isReady;
	effectiveMode;
	triedSourceIds = /* @__PURE__ */ new Set();
	options;
	wsTransport;
	scope = Ue(!0);
	connectionGeneration = 0;
	abortController = new AbortController();
	probedSourceId;
	wasPausedByVisibility = !1;
	wsHandle;
	webrtcHandler;
	mseHandler;
	firstFrameCallbackId;
	backchannelHandler;
	pendingMicTrack = null;
	lastMediaStream = null;
	stopWatchers = [];
	mseMonitorInterval;
	offTabVisible;
	offTabPaused;
	onVideoPauseBound;
	onVideoPlayBound;
	onVideoResizeBound;
	startWsConnectTimeout;
	stopWsConnectTimeout;
	startConnectTimeout;
	stopConnectTimeout;
	startMseConnectTimeout;
	stopMseConnectTimeout;
	startReconnectTimeout;
	stopReconnectTimeout;
	constructor(e) {
		this.options = e;
		let t = Xs();
		if (!t.wsTransport) throw Error("[camera.ui] StreamConnection requires a wsTransport on CameraUiContext — pass `wsTransport` to createCameraUiPlugin.");
		this.target = t.target, this.wsTransport = t.wsTransport;
		let { autoStart: n = !0 } = e;
		this.status = /* @__PURE__ */ V("idle"), this.activeMode = /* @__PURE__ */ V("webrtc"), this.activeResolution = /* @__PURE__ */ V("low-resolution"), this.degradedFrom = /* @__PURE__ */ V(null), this.degradeReason = /* @__PURE__ */ V(null), this.source = /* @__PURE__ */ H(), this.hasVideo = /* @__PURE__ */ V(!1), this.hasAudio = /* @__PURE__ */ V(!1), this.hasBackchannel = /* @__PURE__ */ V(!1), this.isPlaying = /* @__PURE__ */ V(!1), this.error = /* @__PURE__ */ V(), this.probeInfo = /* @__PURE__ */ H(), this.muted = /* @__PURE__ */ V(!0), this.paused = /* @__PURE__ */ V(!1), this.nativeWidth = /* @__PURE__ */ V(0), this.nativeHeight = /* @__PURE__ */ V(0), this.requestedMode = /* @__PURE__ */ V(W(e.mode) ?? "auto"), this.requestedResolution = /* @__PURE__ */ V(W(e.resolution) ?? "high-resolution"), this.camera = Y(() => W(e.camera)), this.videoElement = Y(() => W(e.videoElement)), this.containerElement = Y(() => W(e.containerElement)), this.isReady = Y(() => !!this.camera.value && !!this.videoElement.value && !!this.target.value), this.effectiveMode = Y(() => this.requestedMode.value === "auto" ? this.activeMode.value : this.requestedMode.value), this.scope.run(() => {
			let { onTabPaused: e, onTabVisible: t } = Zc(), r = Ko(() => {
				this.wsHandle?.readyState === WebSocket.CONNECTING && (this.disconnectWebSocket(), !this.abortController.signal.aborted && this.status.value !== "closed" && this.restart());
			}, Qc.WEBRTC.WS_CONNECT_TIMEOUT, { immediate: !1 }), i = Ko(() => {
				this.webrtcHandler && !this.webrtcHandler.isConnected ? this.requestedMode.value === "auto" ? (this.webrtcHandler.close(), this.webrtcHandler = void 0, this.activeMode.value = "mse", this.mseHandler?.isReady ? this.status.value = "connected" : this.startMSE()) : (this.markSourceUndecodable(), this.restart()) : this.status.value === "connected" && !this.isPlaying.value && !this.abortController.signal.aborted && this.sourceLikelyH265() && this.handleNoFramesWhileConnected();
			}, Qc.WEBRTC.CONNECT_TIMEOUT, { immediate: !1 }), a = Ko(() => {
				this.abortController.signal.aborted || this.status.value === "connected" || this.status.value === "closed" || this.mseHandler && !this.mseHandler.isReady && (this.markSourceUndecodable(), this.restart());
			}, Qc.WEBRTC.CONNECT_TIMEOUT, { immediate: !1 }), o = Ko(() => {
				this.abortController.signal.aborted || this.restart();
			}, Qc.WEBRTC.RECONNECT_DELAY, { immediate: !1 });
			this.startWsConnectTimeout = r.start, this.stopWsConnectTimeout = r.stop, this.startConnectTimeout = i.start, this.stopConnectTimeout = i.stop, this.startMseConnectTimeout = a.start, this.stopMseConnectTimeout = a.stop, this.startReconnectTimeout = o.start, this.stopReconnectTimeout = o.stop, this.setupWatchers(), this.offTabPaused = e(() => {
				if ($.debug(`onTabPaused fired — status=${this.status.value}, isReady=${this.isReady.value}, target=${!!this.target.value}`), this.status.value === "idle" || this.status.value === "closed") {
					$.debug(`onTabPaused — already in ${this.status.value}, skipping stop()`);
					return;
				}
				this.wasPausedByVisibility = !0, this.stop(), $.debug("onTabPaused — stop() done, wasPausedByVisibility=true");
			}), this.offTabVisible = t(() => {
				if ($.debug(`onTabVisible fired — wasPausedByVisibility=${this.wasPausedByVisibility}, status=${this.status.value}, isReady=${this.isReady.value}, target=${!!this.target.value}`), !this.wasPausedByVisibility) {
					$.debug("onTabVisible — not paused by visibility, no-op");
					return;
				}
				this.wasPausedByVisibility = !1, this.startWhenReady();
			}), n && Jo(this.isReady, () => {
				(this.status.value === "idle" || this.status.value === "closed") && this.start();
			}, { immediate: !0 });
		});
	}
	async start() {
		if ($.debug(`start() called — status=${this.status.value}, isReady=${this.isReady.value}`), this.status.value !== "idle" && this.status.value !== "closed") {
			$.debug(`start() — skipped, status is ${this.status.value}`);
			return;
		}
		if (!this.isReady.value) {
			$.debug("start() — skipped, isReady=false");
			return;
		}
		this.cleanup(), this.abortController = new AbortController();
		let e = ++this.connectionGeneration;
		this.triedSourceIds.clear(), this.status.value = "connecting", this.error.value = void 0, this.isPlaying.value = !1;
		try {
			let t = this.initializeSource();
			if (t === "unsupported") {
				$.debug("start() — no source with a playable codec"), this.setUnsupported();
				return;
			}
			if (!t) {
				$.debug("start() — no streaming source available"), this.error.value = /* @__PURE__ */ Error("No streaming source available"), this.status.value = "error";
				return;
			}
			for (let t = 0; t < 3; t++) {
				let t = this.source.value?._id, n = await this.probeStream();
				if (e !== this.connectionGeneration) {
					$.debug("start() — generation stale after probe, aborting");
					return;
				}
				n && t && this.probeSaysUnplayable(n) && this.triedSourceIds.add(t);
				let r = this.initializeSource();
				if (r === "unsupported") {
					this.setUnsupported();
					return;
				}
				if (!r) {
					this.error.value = /* @__PURE__ */ Error("No streaming source available"), this.status.value = "error";
					return;
				}
				if (!n || this.source.value?._id === t) break;
			}
			$.debug("start() — connecting WebSocket"), this.connectWebSocket();
		} catch (t) {
			if (e !== this.connectionGeneration) return;
			$.debug("start() — error:", t), this.error.value = t instanceof Error ? t : Error(String(t)), this.status.value = "error";
		}
	}
	stop() {
		if (this.status.value === "closed") {
			$.debug("stop() — already closed, no-op");
			return;
		}
		$.debug(`stop() — was ${this.status.value}, transitioning to closed`), ++this.connectionGeneration, this.status.value = "closed", this.cleanup();
	}
	async setMode(e) {
		if (this.requestedMode.value !== e) {
			if (this.requestedMode.value = e, this.activeMode.value = e === "auto" ? "webrtc" : e, this.status.value === "unsupported") {
				this.stop(), await this.start();
				return;
			}
			this.status.value === "connected" && await this.restart();
		}
	}
	async setResolution(e) {
		if (this.requestedResolution.value === e) return;
		if (this.requestedResolution.value = e, this.status.value === "unsupported") {
			this.stop(), await this.start();
			return;
		}
		let t = this.getSourceForResolution(e);
		t && t !== "unsupported" && t.source._id !== this.source.value?._id && (this.source.value = t.source, this.activeResolution.value = t.effectiveResolution, this.degradedFrom.value = t.degradedFrom, this.degradeReason.value = t.degradedFrom ? "codec" : null, this.status.value === "connected" && await this.restart());
	}
	async setMicrophone(e) {
		if (this.webrtcHandler) {
			await this.webrtcHandler.setMicrophoneTrack(e);
			return;
		}
		this.activeMode.value === "mse" && this.hasBackchannel.value && (this.pendingMicTrack = e, e && !this.backchannelHandler ? await this.startBackchannel() : !e && this.backchannelHandler ? this.closeBackchannel() : this.backchannelHandler?.isConnected && await this.backchannelHandler.setMicrophoneTrack(e));
	}
	setMuted(e) {
		this.muted.value = e;
		let t = this.videoElement.value;
		t && (t.muted = e);
	}
	async play() {
		this.paused.value = !1;
		let e = this.videoElement.value;
		if (e) try {
			await e.play();
		} catch {
			if (!e.muted) {
				e.muted = !0, this.muted.value = !0;
				try {
					await e.play();
				} catch {}
			}
		}
	}
	pause() {
		this.paused.value = !0;
		let e = this.videoElement.value;
		e && e.pause();
	}
	destroy() {
		for (let e of this.stopWatchers) e();
		this.stopWatchers = [], this.offTabVisible?.(), this.offTabVisible = void 0, this.offTabPaused?.(), this.offTabPaused = void 0;
		let e = this.videoElement.value;
		e && (this.onVideoPauseBound && e.removeEventListener("pause", this.onVideoPauseBound), this.onVideoPlayBound && e.removeEventListener("play", this.onVideoPlayBound), this.onVideoResizeBound && e.removeEventListener("resize", this.onVideoResizeBound)), this.stop(), this.scope.stop();
	}
	async restart() {
		this.status.value = "reconnecting", this.isPlaying.value = !1, this.cleanup(), this.abortController = new AbortController();
		let e = ++this.connectionGeneration;
		try {
			await pl(1e3, this.abortController.signal);
		} catch {
			return;
		}
		if (e === this.connectionGeneration) {
			if (!this.isReady.value) {
				this.status.value = "idle";
				return;
			}
			try {
				let e = this.initializeSource();
				if (e === "unsupported") {
					this.setUnsupported();
					return;
				}
				if (!e) {
					this.error.value = /* @__PURE__ */ Error("No streaming source available"), this.status.value = "error";
					return;
				}
				this.connectWebSocket();
			} catch (t) {
				if (e !== this.connectionGeneration) return;
				this.error.value = t instanceof Error ? t : Error(String(t)), this.status.value = "error";
			}
		}
	}
	startWhenReady() {
		if (this.isReady.value) {
			$.debug("startWhenReady — already ready, calling start() now"), this.start();
			return;
		}
		$.debug(`startWhenReady — not ready (camera=${!!this.camera.value}, video=${!!this.videoElement.value}, target=${!!this.target.value}), watching isReady`);
		let e = G(this.isReady, (t) => {
			t && ($.debug("startWhenReady — isReady → true, calling start()"), e(), this.start());
		});
		this.stopWatchers.push(e);
	}
	setupWatchers() {
		let e = G(() => this.target.value?.endpoint.url ?? null, (e, t) => {
			!e || !t || e === t || this.status.value !== "idle" && this.status.value !== "closed" && this.restart();
		});
		this.stopWatchers.push(e);
		let t = G(() => this.camera.value?.sources.value, () => {
			this.status.value === "unsupported" && (this.stop(), this.start());
		});
		this.stopWatchers.push(t);
		let n = G(() => W(this.options.mode), (e) => {
			e !== void 0 && e !== this.requestedMode.value && this.setMode(e);
		});
		this.stopWatchers.push(n);
		let r = G(() => W(this.options.resolution), (e) => {
			e !== void 0 && e !== this.requestedResolution.value && this.setResolution(e);
		});
		this.stopWatchers.push(r);
		let i = G(this.videoElement, (e, t) => {
			t && (this.onVideoPauseBound && t.removeEventListener("pause", this.onVideoPauseBound), this.onVideoPlayBound && t.removeEventListener("play", this.onVideoPlayBound), this.onVideoResizeBound && t.removeEventListener("resize", this.onVideoResizeBound)), e && (this.onVideoPauseBound = () => {
				this.paused.value || e.play().catch(() => {});
			}, this.onVideoPlayBound = () => {
				this.paused.value = !1;
			}, this.onVideoResizeBound = () => {
				e.videoWidth > 0 && e.videoHeight > 0 && (this.nativeWidth.value = e.videoWidth, this.nativeHeight.value = e.videoHeight);
			}, e.addEventListener("pause", this.onVideoPauseBound), e.addEventListener("play", this.onVideoPlayBound), e.addEventListener("resize", this.onVideoResizeBound), e.videoWidth > 0 && e.videoHeight > 0 && (this.nativeWidth.value = e.videoWidth, this.nativeHeight.value = e.videoHeight));
		}, { immediate: !0 });
		this.stopWatchers.push(i);
		let a = G(this.activeMode, (e) => {
			this.stopMseMonitor(), e === "mse" && (this.mseMonitorInterval = setInterval(() => this.monitorMseBuffer(), 1e3));
		}, { immediate: !0 });
		this.stopWatchers.push(a);
		let o = G([
			this.camera,
			this.videoElement,
			() => this.target.value
		], ([e, t, n], [r, i]) => {
			if (e !== r) this.status.value === "connected" ? e && t && n && this.restart() : this.status.value === "unsupported" && e && t && n && (this.stop(), this.start());
			else if (t !== i && t) {
				if (t.srcObject instanceof MediaStream) {
					let e = t.srcObject;
					if (e.active && e.getTracks().some((e) => e.readyState === "live")) {
						hl(t), this.lastMediaStream = e;
						return;
					}
				}
				if (this.status.value === "connected" && this.activeMode.value !== "mse") {
					let e = this.lastMediaStream;
					e?.active && e.getTracks().some((e) => e.readyState === "live") ? (t.srcObject = e, hl(t)) : this.restart();
				} else if (this.status.value === "connected" && this.activeMode.value === "mse") this.restart();
				else if (this.status.value === "connecting" || this.status.value === "reconnecting") {
					let e = G(() => this.isPlaying.value, (t) => {
						let n = this.videoElement.value;
						t && n?.srcObject instanceof MediaStream ? (hl(n), e()) : t && n && !n.srcObject && this.lastMediaStream?.active && (n.srcObject = this.lastMediaStream, hl(n), e());
					}, { immediate: !0 });
					this.stopWatchers.push(e);
				}
			}
		});
		this.stopWatchers.push(o);
	}
	isSourcePlayable(e) {
		if (this.triedSourceIds.has(e._id)) return !1;
		if (e.videoCodec !== "H265") return !0;
		let t = this.requestedMode.value;
		return sl(t === "auto" ? "auto" : t === "mse" ? "mse" : "webrtc");
	}
	getSourceForResolution(e) {
		let t = this.camera.value;
		if (!t) return;
		let n = [
			"high-resolution",
			"mid-resolution",
			"low-resolution"
		], r = Math.max(0, n.indexOf(e)), i = !1;
		for (let a = r; a < n.length; a++) {
			let r = t.sources.value.find((e) => e.role === n[a]);
			if (r) {
				if (!this.isSourcePlayable(r)) {
					i = !0;
					continue;
				}
				return {
					source: r,
					effectiveResolution: n[a],
					degradedFrom: i ? e : null
				};
			}
		}
		let a = t.streamSource.value;
		if (a && this.isSourcePlayable(a)) return {
			source: a,
			effectiveResolution: a.role ?? "low-resolution",
			degradedFrom: i ? e : null
		};
		if (i || a) return "unsupported";
	}
	initializeSource() {
		let e = this.getSourceForResolution(this.requestedResolution.value);
		return e ? e === "unsupported" ? "unsupported" : (this.source.value = e.source, this.activeResolution.value = e.effectiveResolution, this.degradedFrom.value = e.degradedFrom, this.degradeReason.value = e.degradedFrom ? "codec" : null, this.probedSourceId && this.probedSourceId !== e.source._id && (this.probeInfo.value = void 0, this.probedSourceId = void 0, this.hasVideo.value = !1, this.hasAudio.value = !1, this.hasBackchannel.value = !1), !0) : !1;
	}
	setUnsupported() {
		let e = this.camera.value?.sources.value.find((e) => e.videoCodec)?.videoCodec ?? "H265";
		this.error.value = /* @__PURE__ */ Error(`${e} cannot be played on this device`), this.status.value = "unsupported";
	}
	probeSaysUnplayable(e) {
		let t = e.video.filter((e) => e.direction === "sendonly");
		if (!t.length || !t.every((e) => e.codec === "H265")) return !1;
		let n = this.requestedMode.value;
		return !sl(n === "auto" ? "auto" : n === "mse" ? "mse" : "webrtc");
	}
	sourceLikelyH265() {
		let e = this.source.value;
		if (!e) return !1;
		if (e.videoCodec === "H265") return !0;
		if (e.videoCodec !== void 0) return !1;
		let t = this.probeInfo.value?.video.filter((e) => e.direction === "sendonly") ?? [];
		return t.length > 0 && t.every((e) => e.codec === "H265");
	}
	markSourceUndecodable() {
		let e = this.source.value;
		!e || !this.sourceLikelyH265() || this.triedSourceIds.add(e._id);
	}
	handleNoFramesWhileConnected() {
		cl(this.activeMode.value === "mse" ? "mse" : "webrtc"), this.markSourceUndecodable(), this.restart();
	}
	async probeStream() {
		let e = this.camera.value, t = this.source.value;
		if (!(!e || !t || this.abortController.signal.aborted)) try {
			let n = await e.probeStream(t._id, {
				video: !0,
				audio: ["pcma", "opus"],
				microphone: !0
			});
			return n && !this.abortController.signal.aborted && (this.probeInfo.value = n, this.probedSourceId = t._id, this.hasBackchannel.value = n.audio.some((e) => e.direction === "recvonly"), this.hasAudio.value = n.audio.filter((e) => e.direction === "sendonly").length > 0, this.hasVideo.value = n.video.filter((e) => e.direction === "sendonly").length > 0), n;
		} catch {
			return;
		}
	}
	connectWebSocket() {
		this.disconnectWebSocket();
		let e = this.camera.value;
		if (this.abortController.signal.aborted || !e || !this.source.value || !this.target.value) return;
		let t = this.source.value.name ?? this.source.value.role ?? this.source.value._id, n = Qs(e.name.value, t);
		this.startWsConnectTimeout(), this.wsHandle = this.wsTransport.open({
			path: "/api/go2rtc",
			query: { src: n },
			binaryType: "arraybuffer"
		}), this.wsHandle.on("open", () => this.handleWsOpen()), this.wsHandle.on("close", () => this.handleWsClose()), this.wsHandle.on("message", (e) => this.handleWsMessage(e)), this.wsHandle.on("error", () => {});
	}
	disconnectWebSocket() {
		this.stopWsConnectTimeout(), this.wsHandle &&= (this.wsHandle.dispose(), void 0);
	}
	sendWsMessage(e) {
		this.wsHandle?.readyState === WebSocket.OPEN && this.wsHandle.send(JSON.stringify(e));
	}
	handleWsOpen() {
		if (this.abortController.signal.aborted) return;
		this.stopWsConnectTimeout(), this.status.value = "connecting";
		let e = this.effectiveMode.value;
		e === "webrtc" || e === "webrtc/tcp" ? this.startWebRTC(e) : e === "mse" ? this.startMSE() : this.requestedMode.value === "auto" && this.startAutoMode();
	}
	handleWsClose() {
		this.status.value !== "closed" && !this.abortController.signal.aborted && this.startReconnectTimeout();
	}
	handleWsMessage(e) {
		if (!this.abortController.signal.aborted) if (typeof e.data == "string") {
			let t;
			try {
				t = JSON.parse(e.data);
			} catch {
				return;
			}
			this.handleMessage(t);
		} else this.mseHandler && (this.mseHandler.appendBuffer(e.data), this.handleFirstFrame());
	}
	handleMessage(e) {
		switch (e.type) {
			case "webrtc/answer":
			case "webrtc/candidate":
				this.webrtcHandler ? Cl(this.webrtcHandler, e) : this.backchannelHandler && Cl(this.backchannelHandler, e);
				break;
			case "mse":
				this.mseHandler && typeof e.value == "string" && this.mseHandler.initializeBuffer(e.value);
				break;
			case "error": this.requestedMode.value !== "auto" && (this.error.value = Error(e.value), this.status.value = "error");
		}
	}
	async startWebRTC(e) {
		if (this.abortController.signal.aborted) return;
		this.startConnectTimeout(), this.webrtcHandler = xl({
			mode: e,
			signal: this.abortController.signal,
			onConnected: (e) => this.handleWebRTCConnected(e),
			onDisconnected: () => this.handleWebRTCDisconnected(),
			onFailed: () => this.handleWebRTCFailed(),
			onCandidate: (e) => this.sendWsMessage({
				type: "webrtc/candidate",
				value: e
			})
		});
		let t = await this.webrtcHandler.createOffer();
		t && !this.abortController.signal.aborted && this.sendWsMessage({
			type: "webrtc/offer",
			value: t
		});
	}
	handleWebRTCConnected(e) {
		if (this.abortController.signal.aborted) return;
		let t = this.videoElement.value;
		t && (this.activeMode.value = this.requestedMode.value === "auto" ? "webrtc" : this.requestedMode.value, this.lastMediaStream = e, t.srcObject = e, t.muted = this.muted.value, hl(t), this.status.value = "connected", this.handleFirstFrameWebRTC(e), this.requestedMode.value === "auto" && this.mseHandler && (this.mseHandler.close(), this.mseHandler = void 0, this.stopMseConnectTimeout()));
	}
	handleWebRTCDisconnected() {
		this.status.value !== "closed" && !this.abortController.signal.aborted && (this.status.value = "reconnecting", this.requestedMode.value === "auto" && this.mseHandler?.isReady ? (this.webrtcHandler?.close(), this.webrtcHandler = void 0, this.activeMode.value = "mse", this.status.value = "connected") : this.restart());
	}
	handleWebRTCFailed() {
		this.abortController.signal.aborted || (this.stopConnectTimeout(), this.requestedMode.value === "auto" ? (this.webrtcHandler?.close(), this.webrtcHandler = void 0, this.activeMode.value = "mse", this.mseHandler?.isReady ? this.status.value = "connected" : this.startMSE()) : (this.error.value = /* @__PURE__ */ Error("WebRTC connection failed"), this.status.value = "error"));
	}
	startMSE() {
		if (this.mseHandler) return;
		let e = this.videoElement.value;
		if (this.abortController.signal.aborted || !e) return;
		this.mseHandler = ml({
			videoElement: e,
			signal: this.abortController.signal,
			onReady: () => this.handleMSEReady(),
			onFirstData: () => this.handleMSEFirstData(),
			onError: (e) => {
				this.requestedMode.value === "auto" ? this.activeMode.value === "mse" && this.status.value === "connected" && ($.debug("MSE error while active in auto mode — restarting:", e), this.restart()) : (this.error.value = e, this.status.value = "error");
			}
		});
		let t = this.mseHandler.setup();
		t && (this.sendWsMessage({
			type: "mse",
			value: t
		}), this.startMseConnectTimeout());
	}
	handleMSEReady() {
		this.abortController.signal.aborted || (this.stopMseConnectTimeout(), this.requestedMode.value === "auto" && this.webrtcHandler?.isConnected || (this.activeMode.value = "mse", this.status.value = "connected"));
	}
	handleMSEFirstData() {
		if (this.abortController.signal.aborted) return;
		let e = this.videoElement.value;
		e && hl(e);
	}
	async startAutoMode() {
		if (this.abortController.signal.aborted) return;
		let e = this.probeInfo.value ?? await this.probeStream();
		if (e && !ul(e).compatible) {
			this.activeMode.value = "mse", this.startMSE();
			return;
		}
		this.startMSE(), this.startWebRTC("webrtc");
	}
	handleFirstFrame() {
		!this.isPlaying.value && !this.abortController.signal.aborted && (this.stopConnectTimeout(), this.isPlaying.value = !0);
	}
	monitorMseBuffer() {
		let e = this.videoElement.value;
		if (!(!e || this.activeMode.value !== "mse" || !this.isPlaying.value) && e.buffered.length > 0) {
			let t = e.buffered.end(e.buffered.length - 1);
			t - e.currentTime > 1 && (e.currentTime = t);
		}
	}
	stopMseMonitor() {
		this.mseMonitorInterval !== void 0 && (clearInterval(this.mseMonitorInterval), this.mseMonitorInterval = void 0);
	}
	handleFirstFrameWebRTC(e) {
		let t = this.videoElement.value;
		if (this.isPlaying.value || this.abortController.signal.aborted || !t) return;
		if (!e.getVideoTracks()[0]) {
			this.handleFirstFrame();
			return;
		}
		let n = t;
		if (typeof n.requestVideoFrameCallback == "function") this.firstFrameCallbackId = n.requestVideoFrameCallback(() => {
			this.abortController.signal.aborted || this.handleFirstFrame();
		});
		else {
			let e = () => {
				this.abortController.signal.aborted || (t.readyState >= 2 && t.videoWidth > 0 ? this.handleFirstFrame() : this.firstFrameCallbackId = requestAnimationFrame(e));
			};
			this.firstFrameCallbackId = requestAnimationFrame(e);
		}
	}
	cleanup() {
		this.abortController.abort(), this.stopConnectTimeout(), this.stopWsConnectTimeout(), this.stopMseConnectTimeout(), this.stopReconnectTimeout(), this.stopMseMonitor(), this.lastMediaStream = null, this.webrtcHandler?.close(), this.webrtcHandler = void 0, this.mseHandler?.close(), this.mseHandler = void 0, this.closeBackchannel(), this.disconnectWebSocket();
		let e = this.videoElement.value;
		this.firstFrameCallbackId !== void 0 && (e && "cancelVideoFrameCallback" in e ? e.cancelVideoFrameCallback(this.firstFrameCallbackId) : cancelAnimationFrame(this.firstFrameCallbackId), this.firstFrameCallbackId = void 0), e && (e.style.display = "", e.pause(), e.srcObject = null, e.removeAttribute("src"), e.load());
	}
	async startBackchannel() {
		if (this.abortController.signal.aborted || !this.wsHandle || this.wsHandle.readyState !== WebSocket.OPEN) return;
		this.backchannelHandler = Sl({
			signal: this.abortController.signal,
			onCandidate: (e) => this.sendWsMessage({
				type: "webrtc/candidate",
				value: e
			}),
			onConnected: async () => {
				this.pendingMicTrack && this.backchannelHandler && await this.backchannelHandler.setMicrophoneTrack(this.pendingMicTrack);
			},
			onDisconnected: () => {
				this.backchannelHandler = void 0;
			}
		});
		let e = await this.backchannelHandler.createOffer();
		e && !this.abortController.signal.aborted && this.sendWsMessage({
			type: "webrtc/offer",
			value: e
		});
	}
	closeBackchannel() {
		this.backchannelHandler?.close(), this.backchannelHandler = void 0, this.pendingMicTrack = null;
	}
};
function Tl(e) {
	return new wl(e);
}
var El = class {
	streams = /* @__PURE__ */ new Map();
	releaseTimers = /* @__PURE__ */ new Map();
	releaseDelay;
	DEFAULT_RELEASE_DELAY = 2e3;
	constructor(e = {}) {
		this.releaseDelay = e.releaseDelay ?? this.DEFAULT_RELEASE_DELAY;
	}
	has(e) {
		return this.streams.has(e);
	}
	getRefCount(e) {
		return this.streams.get(e)?.refCount ?? 0;
	}
	get(e) {
		return this.streams.get(e);
	}
	acquire(e, t) {
		this.cancelRelease(e);
		let n = this.streams.get(e);
		if (n) return n.refCount++, t && n.consumerContainerRefs.add(t), n;
	}
	register(e, t, n, r, i, a) {
		this.cancelRelease(e);
		let o = {
			stream: t,
			videoElementRef: n,
			cameraDeviceRef: r,
			containerElementRef: i,
			consumerContainerRefs: /* @__PURE__ */ new Set([i]),
			sharedVideoElement: a,
			mediaStream: null,
			refCount: 1
		};
		return this.streams.set(e, o), o;
	}
	updateContainerElement(e, t) {
		let n = this.streams.get(e);
		n && (n.containerElementRef.value = t);
	}
	updateSharedVideoElement(e, t) {
		let n = this.streams.get(e);
		n && (n.sharedVideoElement = t);
	}
	updateMediaStream(e, t) {
		let n = this.streams.get(e);
		n && (n.mediaStream = t);
	}
	release(e, t, n) {
		let r = this.streams.get(e);
		if (r) {
			if (r.refCount--, n) {
				r.consumerContainerRefs.delete(n);
				let e = r.sharedVideoElement, t = n.value, i = e?.parentElement ?? null;
				if (r.refCount > 0 && e && (i === t || i === null || !i.isConnected)) {
					let n = this.pickVisibleConsumer(r, t);
					n && (r.containerElementRef = n.ref, e.parentElement !== n.el && (n.el.appendChild(e), e.play().catch(() => {})));
				}
			}
			if (r.refCount <= 0) {
				let t = setTimeout(() => {
					this.doRelease(e);
				}, this.releaseDelay);
				this.releaseTimers.set(e, t);
			}
		}
	}
	forceRelease(e) {
		this.cancelRelease(e), this.doRelease(e);
	}
	clear() {
		for (let e of this.releaseTimers.values()) clearTimeout(e);
		this.releaseTimers.clear();
		for (let [e, t] of this.streams) Dl(t.stream), this.streams.delete(e);
	}
	getDebugInfo() {
		return Array.from(this.streams.entries()).map(([e, t]) => ({
			cameraName: e,
			refCount: t.refCount,
			mode: t.stream.activeMode.value,
			resolution: t.stream.activeResolution.value
		}));
	}
	pickVisibleConsumer(e, t) {
		let n;
		for (let r of e.consumerContainerRefs) {
			let e = r.value;
			if (!(!e || e === t || !e.isConnected)) {
				if (e.checkVisibility?.() ?? e.offsetParent !== null) return {
					ref: r,
					el: e
				};
				n ??= {
					ref: r,
					el: e
				};
			}
		}
		return n;
	}
	cancelRelease(e) {
		let t = this.releaseTimers.get(e);
		t && (clearTimeout(t), this.releaseTimers.delete(e));
	}
	doRelease(e) {
		let t = this.streams.get(e);
		t && (t.refCount <= 0 && (Dl(t.stream), this.streams.delete(e)), this.releaseTimers.delete(e));
	}
};
function Dl(e) {
	let t = e;
	typeof t.destroy == "function" ? t.destroy() : t.stop();
}
var Ol = new El(), kl = /* @__PURE__ */ new WeakMap(), Al = [], jl = /* @__PURE__ */ H(null);
function Ml() {
	jl.value = Al[Al.length - 1] ?? null;
}
function Nl(e, t = {}) {
	let n = t.mode ?? "fit", r = /* @__PURE__ */ V(!1), i = /* @__PURE__ */ H(null);
	G(() => W(e), (e) => {
		i.value = e ?? null;
	}, { immediate: !0 });
	function a(e) {
		e.key === "Escape" && r.value && s();
	}
	async function o() {
		let e = i.value;
		if (!e || r.value) return;
		let t = document.createElement("div");
		t.className = `cui-fullscreen cui-fullscreen-${n}`, Pl(t, n);
		let o = {
			wrapper: t,
			parent: e.parentElement,
			next: e.nextSibling,
			bodyOverflow: document.body.style.overflow,
			htmlOverflow: document.documentElement.style.overflow
		};
		kl.set(e, o), e.setAttribute("data-cui-fullscreen", n), document.body.appendChild(t), t.appendChild(e), document.body.style.overflow = "hidden", document.documentElement.style.overflow = "hidden", document.addEventListener("keydown", a), Al.push(t), Ml(), r.value = !0;
	}
	async function s() {
		let e = i.value;
		if (!e || !r.value) return;
		let t = kl.get(e);
		if (!t) return;
		kl.delete(e), e.removeAttribute("data-cui-fullscreen"), t.parent && (t.next && t.next.parentNode === t.parent ? t.parent.insertBefore(e, t.next) : t.parent.appendChild(e)), t.wrapper.remove(), document.body.style.overflow = t.bodyOverflow, document.documentElement.style.overflow = t.htmlOverflow, document.removeEventListener("keydown", a);
		let n = Al.indexOf(t.wrapper);
		n !== -1 && Al.splice(n, 1), Ml(), r.value = !1;
	}
	async function c() {
		r.value ? await s() : await o();
	}
	return Lo(() => {
		r.value && i.value && s(), document.removeEventListener("keydown", a);
	}), {
		isFullscreen: Y(() => r.value),
		isSupported: Y(() => !0),
		enter: o,
		exit: s,
		toggle: c
	};
}
function Pl(e, t) {
	let n = {
		position: "fixed",
		top: "0",
		right: "0",
		bottom: "0",
		left: "0",
		zIndex: "2147483647",
		margin: "0",
		background: "black",
		paddingTop: "env(safe-area-inset-top)",
		paddingRight: "env(safe-area-inset-right)",
		paddingBottom: "env(safe-area-inset-bottom)",
		paddingLeft: "env(safe-area-inset-left)",
		boxSizing: "border-box"
	};
	t === "fit" ? Object.assign(e.style, n, {
		display: "flex",
		alignItems: "center",
		justifyContent: "center",
		overflow: "hidden"
	}) : Object.assign(e.style, n, {
		display: "block",
		overflowY: "auto",
		overflowX: "hidden",
		WebkitOverflowScrolling: "touch",
		overscrollBehavior: "contain"
	});
}
var Fl = 75, Il = 500, Ll = 0, Rl = 0;
function zl() {
	let e = performance.now();
	e - Rl > Il && (Ll = 0);
	let t = Ll * Fl;
	return Ll++, Rl = e, t;
}
function Bl(e) {
	return !e || !e.isConnected ? !1 : e.checkVisibility?.() ?? e.offsetParent !== null;
}
function Vl(e) {
	let { activityConfig: t, autoStart: n = !0, isolated: r = !1 } = e, i = () => W(n), a = e.startDelay ?? zl(), o = [], { isConnected: s } = Xs(), c = Y(() => W(e.camera)), l = Y(() => typeof c.value == "string"), u = Y(() => {
		let e = c.value;
		return typeof e == "string" ? e : e.name.value;
	}), { camera: d, isLoading: f } = Cc(Y(() => l.value ? u.value : "")), p = Y(() => l.value && f.value), m = Y(() => l.value ? d.value : c.value), h, g, _, v = /* @__PURE__ */ H(), y = /* @__PURE__ */ H(), b = /* @__PURE__ */ H(), x = /* @__PURE__ */ H(), S = /* @__PURE__ */ H(), ee = /* @__PURE__ */ H(), C = /* @__PURE__ */ V(!1), w = /* @__PURE__ */ V(!1), T = /* @__PURE__ */ V(!1), E = /* @__PURE__ */ V(0), te = /* @__PURE__ */ V(0), D = /* @__PURE__ */ V(!1), ne = /* @__PURE__ */ V(a <= 0);
	a > 0 && (h = setTimeout(() => {
		ne.value = !0;
	}, a)), G(m, (e) => {
		ee.value = e;
	}, { immediate: !0 });
	let O = Y(() => ee.value?.disabled.value === !0), k = Y(() => S.value?.status.value ?? "idle"), A = Y(() => S.value?.isPlaying.value ?? !1), re = Y(() => S.value?.activeMode.value ?? "webrtc"), ie = Y(() => S.value?.activeResolution.value ?? "low-resolution"), j = Y(() => S.value?.degradedFrom.value ?? null), M = Y(() => k.value === "unsupported"), ae = Y(() => S.value?.hasAudio.value ?? !1), oe = Y(() => S.value?.hasBackchannel.value ?? !1), se = Y(() => S.value?.error.value), N = Y(() => k.value === "reconnecting"), P = Y(() => p.value || !A.value && k.value !== "error" && k.value !== "unsupported"), ce = Y(() => ae.value && k.value === "connected"), F = Y(() => !!(typeof navigator < "u" && navigator.mediaDevices) && oe.value), le = Y(() => S.value?.muted.value ?? !0), ue = Y(() => S.value?.paused.value ?? !1), de = Y(() => typeof document < "u" && document.pictureInPictureEnabled && !!b.value), fe = Y(() => b.value), pe = Y(() => y.value ?? v.value), I = Rc({
		initialMode: W(e.activityMode) ?? "always-on",
		config: t,
		onStreamStart: () => {
			O.value || S.value?.start();
		},
		onStreamStop: () => {
			if (C.value) {
				let e = _ ?? u.value;
				if (e && Ol.getRefCount(e) > 1) return;
			}
			S.value?.stop();
		},
		isStreamPlaying: () => A.value
	}), { isFullscreen: me, toggle: he } = Nl(pe);
	function ge() {
		return g = Tl({
			camera: ee,
			videoElement: x,
			containerElement: v,
			mode: Y(() => W(e.mode) ?? "auto"),
			resolution: Y(() => W(e.resolution) ?? "high-resolution"),
			autoStart: !1
		}), g;
	}
	let L = ge();
	function _e() {
		let e = document.createElement("video");
		return e.autoplay = !0, e.playsInline = !0, e.muted = !0, e.disablePictureInPicture = !1, e.preload = "auto", e.poster = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=", e.style.position = "absolute", e.style.width = "100%", e.style.height = "100%", e.style.inset = "0", e.style.objectFit = "fill", e;
	}
	function ve(e, t) {
		e.parentElement && e.parentElement !== t && e.parentElement.removeChild(e), e.parentElement !== t && t.appendChild(e);
	}
	function ye() {
		if (r) return;
		let e = v.value, t = b.value;
		if (!e || !t || t.parentElement === e || !Bl(e) || Bl(t.parentElement)) return;
		ve(t, e), t.play().catch(() => {});
		let n = u.value, i = n ? Ol.get(n) : void 0;
		i && (i.containerElementRef = v);
	}
	function be() {
		D.value = !0;
	}
	function xe() {
		D.value = !1;
	}
	function Se() {
		if (w.value) return;
		let e = v.value, t = m.value;
		if (!e || !t || !s.value) return;
		w.value = !0, C.value = !1, S.value = L;
		let n = _e();
		b.value = n, x.value = n, i() && ne.value && I.mode.value === "always-on" && !O.value && L.start();
	}
	function Ce() {
		if (w.value) return;
		if (r) {
			Se();
			return;
		}
		let e = v.value, t = u.value, n = m.value;
		if (!e || !t || !s.value) return;
		let a = Ol.acquire(t, v);
		if (a) {
			w.value = !0, _ = t, C.value = !0, S.value = a.stream, n && a.cameraDeviceRef && (a.cameraDeviceRef.value = n);
			let r = a.sharedVideoElement;
			r || (r = _e(), a.sharedVideoElement = r, Ol.updateSharedVideoElement(t, r)), a.mediaStream?.active && (r.srcObject = a.mediaStream), e && (a.containerElementRef = v), b.value = r, a.videoElementRef.value = r, Ee(a.stream, r, t), i() && ne.value && I.mode.value === "always-on" && !O.value && (a.stream.activeMode.value === "mse" ? r.play().catch(() => {}) : we(a, r, t));
		} else if (n) {
			w.value = !0, _ = t, C.value = !1, S.value = L;
			let e = _e();
			b.value = e, x.value = e, Ol.register(t, L, x, ee, v, e), i() && ne.value && I.mode.value === "always-on" && !O.value && L.start();
			let n = G(() => L.isPlaying.value, (n) => {
				n && e.srcObject instanceof MediaStream && Ol.updateMediaStream(t, e.srcObject);
			}, { immediate: !0 });
			o.push(n);
			let r = G(() => L.status.value, (n) => {
				n === "connected" && e.srcObject instanceof MediaStream && Ol.updateMediaStream(t, e.srcObject);
			});
			o.push(r);
		}
	}
	function we(e, t, n) {
		if (!e) return;
		let r = e.stream, i = r.activeMode.value, a = r.status.value, o = e.mediaStream?.active && e.mediaStream.getTracks().some((e) => e.readyState === "live");
		i === "mse" ? (Ol.updateMediaStream(n, null), r.restart()) : o && e.mediaStream ? (t.srcObject = e.mediaStream, t.play().catch(() => {})) : a === "idle" || a === "closed" ? (r.start(), Te(r, t, n)) : (a === "connected" && r.restart(), Te(r, t, n));
	}
	function Te(e, t, n) {
		let r = G([() => e.isPlaying.value, () => e.status.value], ([e, i]) => {
			if (i === "connected" || e) {
				let e = Ol.get(n)?.mediaStream;
				e?.active && e.getTracks().some((e) => e.readyState === "live") ? (t.srcObject = e, t.play().catch(() => {}), r()) : t.srcObject instanceof MediaStream && (Ol.updateMediaStream(n, t.srcObject), t.play().catch(() => {}), r());
			}
		}, { immediate: !0 });
		o.push(r);
	}
	function Ee(e, t, n) {
		let r = e.status.value !== "connected", i = G(() => e.status.value, (e) => {
			e === "reconnecting" || e === "connecting" ? r = !0 : e === "connected" && r && (r = !1, setTimeout(() => {
				t.srcObject instanceof MediaStream && (Ol.updateMediaStream(n, t.srcObject), t.play().catch(() => {}));
			}, 100));
		}, { immediate: !0 });
		o.push(i);
		let a = G(() => e.isPlaying.value, (r) => {
			r && e.activeMode.value !== "mse" && t.srcObject instanceof MediaStream && (Ol.updateMediaStream(n, t.srcObject), t.play().catch(() => {}));
		}, { immediate: !0 });
		o.push(a);
	}
	async function De() {
		O.value || (I.inStandby.value ? I.resumeFromStandby() : await S.value?.start());
	}
	function Oe() {
		S.value?.stop();
	}
	async function ke() {
		await S.value?.restart();
	}
	function Ae() {
		O.value || I.resumeFromStandby();
	}
	async function je(e) {
		let t = u.value;
		t && Ol.updateMediaStream(t, null), await S.value?.setMode(e);
	}
	async function Me(e) {
		await S.value?.setResolution(e);
	}
	async function Ne(e) {
		await S.value?.setMicrophone(e);
	}
	function Pe(e) {
		I.setMode(e);
	}
	function Fe(e) {
		I.reportActivity(e);
	}
	function Ie(e) {
		S.value?.setMuted(e);
		let t = b.value;
		t && (t.muted = e);
	}
	async function Le() {
		await S.value?.play();
	}
	function Re() {
		S.value?.pause();
	}
	function ze() {
		document.pictureInPictureElement ? document.exitPictureInPicture() : document.pictureInPictureEnabled && b.value && b.value.requestPictureInPicture();
	}
	function Be() {
		let e = b.value;
		if (!e || e.videoWidth === 0) return null;
		let t = document.createElement("canvas");
		return t.width = e.videoWidth, t.height = e.videoHeight, t.getContext("2d")?.drawImage(e, 0, 0), t.toDataURL("image/png");
	}
	function Ve() {
		if (T.value) return;
		T.value = !0, h &&= (clearTimeout(h), void 0), S.value?.setMuted(!0);
		let e = b.value;
		e && (e.muted = !0);
		for (let e of o) e();
		if (o.length = 0, r) g?.destroy();
		else {
			let e = _, t = b.value;
			e && w.value && Ol.release(e, t, v), (!w.value || S.value !== L) && g?.destroy();
		}
		I.dispose();
	}
	function R(t) {
		let n = W(e.canvasStyle), r = W(e.canvasClass);
		if (n) if (typeof n == "string") t.style.cssText += ";" + n;
		else if (Array.isArray(n)) for (let e of n) typeof e == "string" ? t.style.cssText += ";" + e : e && Object.assign(t.style, e);
		else Object.assign(t.style, n);
		if (r) if (typeof r == "string") t.className = r;
		else if (Array.isArray(r)) t.className = r.filter(Boolean).join(" ");
		else for (let [e, n] of Object.entries(r)) t.classList.toggle(e, !!n);
	}
	if (!r && typeof IntersectionObserver < "u") {
		let e, t = G(v, (t) => {
			e?.disconnect(), e = void 0, t && (e = new IntersectionObserver((e) => {
				e.some((e) => e.isIntersecting) && ye();
			}), e.observe(t));
		}, { immediate: !0 });
		o.push(() => {
			t(), e?.disconnect();
		});
	}
	if (e.canvasStyle !== void 0 || e.canvasClass !== void 0) {
		let e, t = G(v, (t) => {
			if (e?.(), e = void 0, !t) return;
			Array.from(t.querySelectorAll("canvas")).forEach((e) => {
				R(e);
			});
			let n = new MutationObserver((e) => {
				for (let t of e) Array.from(t.addedNodes).forEach((e) => {
					e instanceof HTMLCanvasElement ? R(e) : e instanceof HTMLElement && Array.from(e.querySelectorAll("canvas")).forEach((e) => R(e));
				});
			});
			n.observe(t, {
				childList: !0,
				subtree: !0
			}), e = () => n.disconnect();
		}, { immediate: !0 });
		o.push(() => {
			t(), e?.();
		});
	}
	if (e.videoStyle !== void 0 || e.videoClass !== void 0) {
		let t = G([
			b,
			() => W(e.videoStyle),
			() => W(e.videoClass)
		], ([e, t, n]) => {
			if (e) {
				if (t) if (typeof t == "string") e.style.cssText += ";" + t;
				else if (Array.isArray(t)) for (let n of t) typeof n == "string" ? e.style.cssText += ";" + n : n && Object.assign(e.style, n);
				else Object.assign(e.style, t);
				if (n) if (typeof n == "string") e.className = n;
				else if (Array.isArray(n)) e.className = n.filter(Boolean).join(" ");
				else for (let [t, r] of Object.entries(n)) e.classList.toggle(t, r);
			}
		}, { immediate: !0 });
		o.push(t);
	}
	let He = G([() => S.value?.nativeWidth.value, () => S.value?.nativeHeight.value], ([e, t]) => {
		e && e > 0 && (E.value = e), t && t > 0 && (te.value = t);
	});
	o.push(He);
	let Ue = G(b, (e, t) => {
		t && (t.removeEventListener("enterpictureinpicture", be), t.removeEventListener("leavepictureinpicture", xe)), e && (e.addEventListener("enterpictureinpicture", be), e.addEventListener("leavepictureinpicture", xe));
	}, { immediate: !0 });
	return o.push(Ue), G([v, b], ([e, t]) => {
		e && t && ve(t, e);
	}, { immediate: !0 }), G(() => W(e.activityMode), (e) => {
		e && e !== I.mode.value && I.setMode(e);
	}), G([
		v,
		m,
		s,
		ne
	], () => {
		w.value ? ne.value && i() && I.mode.value === "always-on" && !A.value && k.value === "idle" && !O.value && S.value?.start() : Ce();
	}, { immediate: !0 }), G(O, (e, t) => {
		w.value && (!t && e ? S.value?.stop() : t && !e && i() && S.value?.restart());
	}), Ar(Ve), Lo(Ve), {
		status: k,
		isPlaying: A,
		activeMode: re,
		activeResolution: ie,
		degradedFrom: j,
		unsupported: M,
		hasAudio: ae,
		hasBackchannel: oe,
		error: se,
		isReconnecting: N,
		activityMode: I.mode,
		inStandby: I.inStandby,
		hasActivity: I.hasActivity,
		isBusy: P,
		hasSound: ce,
		hasIntercom: F,
		videoElement: b,
		containerElement: v,
		fullscreenElement: y,
		renderElement: fe,
		stream: S,
		muted: le,
		paused: ue,
		nativeWidth: E,
		nativeHeight: te,
		isPip: D,
		supportsPip: de,
		isFullscreen: me,
		start: De,
		stop: Oe,
		restart: ke,
		resumeFromStandby: Ae,
		setMode: je,
		setResolution: Me,
		setMicrophone: Ne,
		setActivityMode: Pe,
		reportActivity: Fe,
		setMuted: Ie,
		play: Le,
		pause: Re,
		togglePip: ze,
		isCameraDisabled: O,
		toggleFullscreen: he,
		captureScreenshot: Be
	};
}
//#endregion
//#region src/assets/logo.svg?url
var Hl = "data:image/svg+xml,%3csvg%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20viewBox='0%200%20233.63%20233.63'%3e%3cdefs%3e%3cstyle%3e.cls-1{fill:url(%23dark_wine);}.cls-2{fill:url(%23light_wine);}.cls-3{fill:none;stroke:%23000;stroke-miterlimit:10;opacity:0;}.cls-4{fill:%23c5c6c8;}.cls-5{fill:%231a1e21;stroke:%233a3a3a;stroke-width:2px;}.cls-6{fill:%23fff;}%3c/style%3e%3clinearGradient%20id='dark_wine'%20x1='87.36'%20y1='158.67'%20x2='87.36'%20y2='59.85'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20offset='0'%20stop-color='%23730000'/%3e%3cstop%20offset='0.49'%20stop-color='%23a51733'/%3e%3c/linearGradient%3e%3clinearGradient%20id='light_wine'%20x1='113.06'%20y1='197.59'%20x2='113.06'%20y2='80.87'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20offset='0'%20stop-color='%23f44a6b'/%3e%3cstop%20offset='0.28'%20stop-color='%23df294c'/%3e%3c/linearGradient%3e%3c/defs%3e%3cg%20id='CameraUI_U'%3e%3cpath%20id='U_Left'%20class='cls-1'%20d='M47.05,119.47s7.58,16,14.12,23.42a45.28,45.28,0,0,0,16.37,11.86A49.46,49.46,0,0,0,99,158.62c9.43-.46,20.55-3.87,29.24-11.86-3.9,2.5-9.87,5.1-15.9,4.77a25.63,25.63,0,0,1-18.38-9.09c-9.39-10.31-7.62-28.35-7.75-32.68-.35-11.42.77-21.92-1.76-36.19-.46-2.64-1.79-5.19-4.55-8-1.83-1.86-8.4-5.75-13.42-5.74-7.31,0-12.95,3.71-15.38,7.84-2,3.41-3.06,4.22-4.23,25.08a217.23,217.23,0,0,0,.22,26.76Z'%20transform='translate(0.5%200.5)'/%3e%3cpath%20id='U_Right'%20class='cls-2'%20d='M144.12,89.6a16.24,16.24,0,0,1,4.06-4.9c4.16-3.4,9-3.67,10.92-3.82a19.7,19.7,0,0,1,12.53,4.58c1.19,1,6.11,5.58,7.13,17.29.73,8.51,3.31,65.93-37,87.14-4.22,2.22-18,9.25-35.66,7.38a62.43,62.43,0,0,1-20.8-6.11,65.8,65.8,0,0,1-18.89-14.23c-20.21-21.67-19.36-57.46-19.36-57.46s7.58,16,14.12,23.42a45.28,45.28,0,0,0,16.37,11.86A49.46,49.46,0,0,0,99,158.62c11.66-.57,25.93-5.64,35-18.32C143.52,126.8,138.46,100.51,144.12,89.6Z'%20transform='translate(0.5%200.5)'/%3e%3c/g%3e%3cg%20id='CameraUI_Lens'%3e%3ccircle%20id='ellipse'%20class='cls-3'%20cx='116.81'%20cy='116.81'%20r='116.31'/%3e%3cg%20id='lens'%3e%3ccircle%20id='lens_bg'%20class='cls-4'%20cx='159.13'%20cy='58.39'%20r='18.66'/%3e%3cpath%20id='lens_inner'%20class='cls-5'%20d='M169.64,58.31a11,11,0,1,1-22,0c0-6.08,4.93-11.86,11-11.86S169.64,52.23,169.64,58.31Z'%20transform='translate(0.5%200.5)'/%3e%3cg%20id='reflections'%3e%3cellipse%20id='dot_1'%20class='cls-6'%20cx='174.36'%20cy='53.69'%20rx='1.84'%20ry='1.42'/%3e%3cellipse%20id='dot_2'%20class='cls-6'%20cx='174.36'%20cy='57.08'%20rx='1.84'%20ry='1.42'/%3e%3cellipse%20id='dot_3'%20class='cls-6'%20cx='174.36'%20cy='60.46'%20rx='1.84'%20ry='1.42'/%3e%3ccircle%20id='dot_4'%20class='cls-6'%20cx='164.09'%20cy='63.77'%20r='1.66'/%3e%3cpath%20id='wide_1'%20class='cls-6'%20d='M156.63,48.9c-1.07-.88-5.52,3.09-6.31,5.43a1.53,1.53,0,0,0,0,1.26c.43.69,1.73.61,2.19.54,2.68-.44,4.71-4.09,4.8-4.37A3.21,3.21,0,0,0,156.63,48.9Z'%20transform='translate(0.5%200.5)'/%3e%3c/g%3e%3c/g%3e%3c/g%3e%3c/svg%3e", Ul = Symbol("cameraui-card-hass"), Wl = Symbol("cameraui-card-config"), Gl = Symbol("cameraui-grid-config"), Kl = {
	viewBox: "0 0 24 24",
	width: "1.2em",
	height: "1.2em"
};
function ql(e, t) {
	return K(), q("svg", Kl, [...t[0] ||= [J("path", {
		fill: "currentColor",
		d: "m12 5.69l5 4.5V18h-2v-6H9v6H7v-7.81zM12 3L2 12h3v8h6v-6h2v6h6v-8h3"
	}, null, -1)]]);
}
var Jl = fn({
	name: "mdi-home-outline",
	render: ql
}), Yl = { class: "pointer-events-none absolute inset-0 z-10" }, Xl = 36, Zl = 44, Ql = 6, $l = 200, eu = .05, tu = /* @__PURE__ */ dr({
	__name: "CardPtz",
	props: {
		entity: {},
		caps: {}
	},
	setup(e) {
		let t = e, n = er(Ul), r = /* @__PURE__ */ V(), i = /* @__PURE__ */ V(), a = /* @__PURE__ */ nn({
			x: 0,
			y: 0
		}), o = /* @__PURE__ */ V(0), s = Y(() => t.caps.includes("pan")), c = Y(() => t.caps.includes("tilt")), l = Y(() => t.caps.includes("zoom")), u = Y(() => t.caps.includes("home")), d = Y(() => s.value || c.value), f = 0, p = {
			pan: 0,
			tilt: 0,
			zoom: 0
		}, m = !1;
		function h(e) {
			return Math.round(e * 100) / 100;
		}
		function g(e) {
			n?.value?.callService("cameraui", "ptz", e, { entity_id: t.entity });
		}
		function _(e, t, n) {
			let r = Date.now();
			!(Math.abs(e - p.pan) > eu || Math.abs(t - p.tilt) > eu || Math.abs(n - p.zoom) > eu) || r - f < $l || (f = r, p = {
				pan: e,
				tilt: t,
				zoom: n
			}, g({
				action: "continuous",
				pan: e,
				tilt: t,
				zoom: n
			}));
		}
		function v() {
			m && (m = !1, p = {
				pan: 0,
				tilt: 0,
				zoom: 0
			}, g({ action: "stop" }));
		}
		function y(e) {
			let t = r.value;
			if (!t) return;
			t.setPointerCapture(e.pointerId);
			let n = t.getBoundingClientRect(), i = n.left + n.width / 2, o = n.top + n.height / 2, l = !1, d = (e) => {
				let t = e.clientX - i, n = e.clientY - o;
				if (!l && Math.hypot(t, n) < Ql) return;
				l = !0, m = !0;
				let r = Math.hypot(t, n);
				r > Xl && (t = t / r * Xl, n = n / r * Xl), a.x = t, a.y = n, _(s.value ? h(t / Xl) : 0, c.value ? h(-n / Xl) : 0, 0);
			}, f = () => {
				t.removeEventListener("pointermove", d), t.removeEventListener("pointerup", f), t.removeEventListener("pointercancel", f), a.x = 0, a.y = 0, l ? v() : u.value && g({ action: "home" });
			};
			t.addEventListener("pointermove", d), t.addEventListener("pointerup", f), t.addEventListener("pointercancel", f);
		}
		function b(e) {
			let t = i.value;
			if (!t) return;
			t.setPointerCapture(e.pointerId);
			let n = t.getBoundingClientRect(), r = n.top + n.height / 2, a = (e) => {
				m = !0;
				let t = Math.max(-44, Math.min(Zl, e.clientY - r));
				o.value = t, _(0, 0, h(-t / Zl));
			}, s = () => {
				t.removeEventListener("pointermove", a), t.removeEventListener("pointerup", s), t.removeEventListener("pointercancel", s), o.value = 0, v();
			};
			t.addEventListener("pointermove", a), t.addEventListener("pointerup", s), t.addEventListener("pointercancel", s);
		}
		return Ar(v), (e, t) => (K(), q("div", Yl, [U(l) ? (K(), q("div", {
			key: 0,
			ref_key: "zoomEl",
			ref: i,
			class: "cui-ptz-track pointer-events-auto absolute bottom-16 left-3 h-28 w-10",
			onPointerdown: b
		}, [
			t[0] ||= J("span", { class: "cui-ptz-mark top-1.5" }, "+", -1),
			t[1] ||= J("span", { class: "cui-ptz-mark bottom-1.5" }, "−", -1),
			J("div", {
				class: "cui-ptz-knob",
				style: De({ transform: `translate(-50%, calc(-50% + ${U(o)}px))` })
			}, null, 4)
		], 544)) : _a("", !0), U(d) ? (K(), q("div", {
			key: 1,
			ref_key: "padEl",
			ref: r,
			class: "cui-ptz-pad pointer-events-auto absolute bottom-16 right-3 h-24 w-24",
			onPointerdown: y
		}, [J("div", {
			class: "cui-ptz-knob",
			style: De({ transform: `translate(calc(-50% + ${U(a).x}px), calc(-50% + ${U(a).y}px))` })
		}, [U(u) ? (K(), sa(U(Jl), {
			key: 0,
			class: "cui-ptz-knob-icon"
		})) : _a("", !0)], 4)], 544)) : _a("", !0)]));
	}
}), nu = /* @__PURE__ */ dr({
	__name: "CardSpinner",
	props: { size: { default: 30 } },
	setup(e) {
		return (t, n) => (K(), q("svg", {
			class: "cui-spin",
			viewBox: "25 25 50 50",
			style: De({
				width: `${e.size}px`,
				height: `${e.size}px`
			})
		}, [...n[0] ||= [J("circle", {
			class: "cui-spin-circle",
			cx: "50",
			cy: "50",
			r: "20",
			fill: "none",
			"stroke-width": "5",
			"stroke-miterlimit": "10"
		}, null, -1)]], 4));
	}
});
//#endregion
//#region src/device.ts
function ru(e, t) {
	let n = Y(() => e.value.camera_name ?? ""), r = Y(() => (e.value.sources ?? []).map((e) => ({
		_id: e.id ?? e.name ?? "",
		name: e.name,
		role: e.role
	})));
	function i(e) {
		return Y(() => r.value.find((t) => t.role === e));
	}
	let a = i("high-resolution"), o = i("mid-resolution"), s = i("low-resolution"), c = Y(() => !1);
	async function l(n) {
		let r = t(), i = e.value, a = i.camera_name, o = i.entry_id;
		if (!r || !a || !o) return;
		let s = i.sources?.find((e) => (e.id ?? e.name) === n) ?? i.sources?.[0], c = s?.name ?? s?.id;
		if (!c) return;
		let l = `/api/cameraui/probe/${o}/${encodeURIComponent(a)}/${encodeURIComponent(c)}`;
		try {
			let e = await r.callWS({
				type: "auth/sign_path",
				path: l,
				expires: 30
			}), t = await fetch(r.hassUrl(e.path));
			if (!t.ok) return;
			let n = await t.json(), i = [];
			return n.has_audio && i.push({ direction: "sendonly" }), n.has_backchannel && i.push({ direction: "recvonly" }), {
				sdp: "",
				audio: i,
				video: n.has_video ? [{ direction: "sendonly" }] : []
			};
		} catch {
			return;
		}
	}
	return {
		id: e.value.camera_name ?? "cameraui-card",
		name: n,
		room: /* @__PURE__ */ V(""),
		nativeId: /* @__PURE__ */ V(void 0),
		disabled: /* @__PURE__ */ V(!1),
		snooze: /* @__PURE__ */ V(!1),
		isCloud: /* @__PURE__ */ V(!1),
		connected: /* @__PURE__ */ V(!0),
		frameWorkerConnected: /* @__PURE__ */ V(!1),
		sources: r,
		streamSource: Y(() => a.value ?? r.value[0]),
		snapshotSource: Y(() => void 0),
		highResolutionSource: a,
		midResolutionSource: o,
		lowResolutionSource: s,
		capabilities: /* @__PURE__ */ V([]),
		hasLight: c,
		hasSiren: c,
		hasDoorbell: c,
		hasBattery: c,
		hasAudioSensor: c,
		hasMotionSensor: c,
		hasObjectSensor: c,
		hasPtz: c,
		camera: /* @__PURE__ */ H({}),
		snapshot: /* @__PURE__ */ H(void 0),
		snapshotLoading: /* @__PURE__ */ V(!1),
		fetchSnapshot: async () => void 0,
		probeStream: l,
		streamUrl: async () => void 0,
		refreshStates: async () => {},
		reconnect: async () => {},
		close: async () => {}
	};
}
//#endregion
//#region ~icons/basil/pause-solid
var iu = {
	viewBox: "0 0 24 24",
	width: "1.2em",
	height: "1.2em"
};
function au(e, t) {
	return K(), q("svg", iu, [...t[0] ||= [J("path", {
		fill: "currentColor",
		d: "M17.276 5.47c.435.16.724.575.724 1.039V17.49c0 .464-.29.879-.724 1.039a3.7 3.7 0 0 1-2.552 0A1.11 1.11 0 0 1 14 17.491V6.51c0-.464.29-.879.724-1.04a3.7 3.7 0 0 1 2.552 0m-8 0c.435.16.724.575.724 1.039V17.49c0 .464-.29.879-.724 1.039a3.7 3.7 0 0 1-2.552 0A1.11 1.11 0 0 1 6 17.491V6.51c0-.464.29-.879.724-1.04a3.7 3.7 0 0 1 2.552 0"
	}, null, -1)]]);
}
var ou = fn({
	name: "basil-pause-solid",
	render: au
}), su = {
	viewBox: "0 0 24 24",
	width: "1.2em",
	height: "1.2em"
};
function cu(e, t) {
	return K(), q("svg", su, [...t[0] ||= [J("path", {
		fill: "currentColor",
		d: "M19.266 13.516a1.917 1.917 0 0 0 0-3.032A35.8 35.8 0 0 0 9.35 5.068l-.653-.232c-1.248-.443-2.567.401-2.736 1.69a42.5 42.5 0 0 0 0 10.948c.17 1.289 1.488 2.133 2.736 1.69l.653-.232a35.8 35.8 0 0 0 9.916-5.416"
	}, null, -1)]]);
}
var lu = fn({
	name: "basil-play-solid",
	render: cu
}), uu = {
	viewBox: "0 0 16 16",
	width: "1.2em",
	height: "1.2em"
};
function du(e, t) {
	return K(), q("svg", uu, [...t[0] ||= [J("path", {
		fill: "currentColor",
		d: "M3.5 2A2.5 2.5 0 0 0 1 4.5v5A2.5 2.5 0 0 0 3.5 12H7v-2a2 2 0 0 1 2-2h5V4.5A2.5 2.5 0 0 0 11.5 2zM8 10a1 1 0 0 1 1-1h5a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1z"
	}, null, -1)]]);
}
var fu = fn({
	name: "fluent-picture-in-picture-16-filled",
	render: du
}), pu = {
	viewBox: "0 0 16 16",
	width: "1.2em",
	height: "1.2em"
};
function mu(e, t) {
	return K(), q("svg", pu, [...t[0] ||= [J("path", {
		fill: "currentColor",
		d: "M1 4.5A2.5 2.5 0 0 1 3.5 2h8A2.5 2.5 0 0 1 14 4.5V8h-1V4.5A1.5 1.5 0 0 0 11.5 3h-8A1.5 1.5 0 0 0 2 4.5v5A1.5 1.5 0 0 0 3.5 11H7v1H3.5A2.5 2.5 0 0 1 1 9.5zM9 9a1 1 0 0 0-1 1v3a1 1 0 0 0 1 1h5a1 1 0 0 0 1-1v-3a1 1 0 0 0-1-1z"
	}, null, -1)]]);
}
var hu = fn({
	name: "fluent-picture-in-picture-16-regular",
	render: mu
}), gu = {
	viewBox: "0 0 32 32",
	width: "1.2em",
	height: "1.2em"
};
function _u(e, t) {
	return K(), q("svg", gu, [...t[0] ||= [J("path", {
		fill: "currentColor",
		d: "m20.923 22.337l7.37 7.37a1 1 0 0 0 1.414-1.414l-26-26a1 1 0 0 0-1.414 1.414L4.884 6.3A4.5 4.5 0 0 0 2 10.5v11A4.5 4.5 0 0 0 6.5 26h10c2.2 0 4.03-1.578 4.423-3.663m1.577-3.374l5.52 5.519c1.056-.134 1.976-1.017 1.976-2.236V9.754c0-1.814-2.036-2.882-3.528-1.852l-3.968 2.74zM9.537 6L21 17.463V10.5A4.5 4.5 0 0 0 16.5 6z"
	}, null, -1)]]);
}
var vu = fn({
	name: "fluent-video-off-32-filled",
	render: _u
}), yu = {
	viewBox: "0 0 16 16",
	width: "1.2em",
	height: "1.2em"
};
function bu(e, t) {
	return K(), q("svg", yu, [...t[0] ||= [J("path", {
		fill: "currentColor",
		d: "M8 1a2 2 0 0 0-2 2v4a2 2 0 1 0 4 0V3a2 2 0 0 0-2-2"
	}, null, -1), J("path", {
		fill: "currentColor",
		d: "M4.5 7A.75.75 0 0 0 3 7a5 5 0 0 0 4.25 4.944V13.5h-1.5a.75.75 0 0 0 0 1.5h4.5a.75.75 0 0 0 0-1.5h-1.5v-1.556A5 5 0 0 0 13 7a.75.75 0 0 0-1.5 0a3.5 3.5 0 1 1-7 0"
	}, null, -1)]]);
}
var xu = fn({
	name: "heroicons-microphone-16-solid",
	render: bu
}), Su = {
	viewBox: "0 0 16 16",
	width: "1.2em",
	height: "1.2em"
};
function Cu(e, t) {
	return K(), q("svg", Su, [...t[0] ||= [J("path", {
		fill: "currentColor",
		d: "M7.557 2.066A.75.75 0 0 1 8 2.75v10.5a.75.75 0 0 1-1.248.56L3.59 11H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h1.59l3.162-2.81a.75.75 0 0 1 .805-.124m5.393.984a.75.75 0 1 0-1.06 1.06a5.5 5.5 0 0 1 0 7.78a.75.75 0 1 0 1.06 1.06a7 7 0 0 0 0-9.9"
	}, null, -1), J("path", {
		fill: "currentColor",
		d: "M10.828 5.172a.75.75 0 1 0-1.06 1.06a2.5 2.5 0 0 1 0 3.536a.75.75 0 1 0 1.06 1.06a4 4 0 0 0 0-5.656"
	}, null, -1)]]);
}
var wu = fn({
	name: "heroicons-speaker-wave-16-solid",
	render: Cu
}), Tu = {
	viewBox: "0 0 16 16",
	width: "1.2em",
	height: "1.2em"
};
function Eu(e, t) {
	return K(), q("svg", Tu, [...t[0] ||= [J("path", {
		fill: "currentColor",
		d: "M7.557 2.066A.75.75 0 0 1 8 2.75v10.5a.75.75 0 0 1-1.248.56L3.59 11H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h1.59l3.162-2.81a.75.75 0 0 1 .805-.124M11.28 5.72a.75.75 0 1 0-1.06 1.06L11.44 8l-1.22 1.22a.75.75 0 1 0 1.06 1.06l1.22-1.22l1.22 1.22a.75.75 0 1 0 1.06-1.06L13.56 8l1.22-1.22a.75.75 0 0 0-1.06-1.06L12.5 6.94z"
	}, null, -1)]]);
}
var Du = fn({
	name: "heroicons-speaker-x-mark-16-solid",
	render: Eu
}), Ou = {
	viewBox: "0 0 24 24",
	width: "1.2em",
	height: "1.2em"
};
function ku(e, t) {
	return K(), q("svg", Ou, [...t[0] ||= [J("path", {
		fill: "currentColor",
		d: "M13 11h5l-1.5-1.5l1.42-1.42L21.84 12l-3.92 3.92l-1.42-1.42L18 13h-5v5l1.5-1.5l1.42 1.42L12 21.84l-3.92-3.92L9.5 16.5L11 18v-5H6l1.5 1.5l-1.42 1.42L2.16 12l3.92-3.92L7.5 9.5L6 11h5V6L9.5 7.5L8.08 6.08L12 2.16l3.92 3.92L14.5 7.5L13 6z"
	}, null, -1)]]);
}
var Au = fn({
	name: "mdi-arrow-all",
	render: ku
}), ju = {
	viewBox: "0 0 24 24",
	width: "1.2em",
	height: "1.2em"
};
function Mu(e, t) {
	return K(), q("svg", ju, [...t[0] ||= [J("path", {
		fill: "none",
		stroke: "currentColor",
		"stroke-linecap": "round",
		"stroke-linejoin": "round",
		"stroke-width": "3",
		d: "M8 4v3a1 1 0 0 1-1 1H4m4 12v-3a1 1 0 0 0-1-1H4M16 4v3a1 1 0 0 0 1 1h3m-4 12v-3a1 1 0 0 1 1-1h3"
	}, null, -1)]]);
}
var Nu = fn({
	name: "mingcute-fullscreen-exit-fill",
	render: Mu
}), Pu = {
	viewBox: "0 0 24 24",
	width: "1.2em",
	height: "1.2em"
};
function Fu(e, t) {
	return K(), q("svg", Pu, [...t[0] ||= [J("path", {
		fill: "none",
		stroke: "currentColor",
		"stroke-linecap": "round",
		"stroke-linejoin": "round",
		"stroke-width": "3",
		d: "M4 8V5a1 1 0 0 1 1-1h3M4 16v3a1 1 0 0 0 1 1h3M20 8V5a1 1 0 0 0-1-1h-3m4 12v3a1 1 0 0 1-1 1h-3"
	}, null, -1)]]);
}
var Iu = fn({
	name: "mingcute-fullscreen-fill",
	render: Fu
}), Lu = ["src"], Ru = {
	key: 1,
	class: "pointer-events-none absolute inset-0 flex items-center justify-center"
}, zu = ["src"], Bu = ["aria-label"], Vu = { class: "flex h-14 w-14 items-center justify-center rounded-full bg-black/45 pl-1 text-white transition group-hover/tap:scale-105" }, Hu = { class: "pointer-events-none absolute bottom-2.5 left-2.5 flex items-center" }, Uu = {
	key: 0,
	class: "flex h-6 w-6 items-center justify-center rounded-[10px] bg-black/50"
}, Wu = {
	key: 1,
	class: "rounded-[10px] bg-black/50 px-2 py-0.5 text-xs font-semibold text-white"
}, Gu = {
	key: 3,
	class: "pointer-events-none absolute inset-0 z-20 flex items-center justify-center"
}, Ku = {
	key: 4,
	class: "pointer-events-none absolute inset-0 z-20 flex flex-col items-center justify-center gap-2 px-4 text-center text-white/60"
}, qu = { class: "text-xs" }, Ju = {
	key: 1,
	class: "overflow-hidden text-ellipsis whitespace-nowrap"
}, Yu = ["title"], Xu = ["title"], Zu = ["disabled"], Qu = "flex h-9 w-9 shrink-0 cursor-pointer items-center justify-center rounded-md text-white transition-colors hover:bg-white/15 disabled:cursor-default disabled:opacity-40", $u = "flex h-7 cursor-pointer items-center rounded-md bg-black/40 px-2 text-[11px] font-semibold text-white transition-colors hover:bg-black/60", ed = /* @__PURE__ */ dr({
	__name: "CardPlayer",
	props: {
		attributes: {},
		entity: {},
		poster: {},
		title: {},
		source: {},
		mode: {},
		autostart: { type: Boolean },
		snapshotInterval: {},
		lang: {}
	},
	setup(e) {
		let t = e, n = er(Ul), r = Vl({
			camera: ru(Y(() => t.attributes), () => n?.value),
			mode: t.mode ?? "auto",
			resolution: t.source ?? "high-resolution",
			autoStart: !1,
			videoClass: "cui-video",
			isolated: !0
		}), { status: i, isReconnecting: a, activeMode: o, activeResolution: s, muted: c, isPip: l, nativeWidth: u, error: d, hasIntercom: f, hasAudio: p } = r, m = {
			"high-resolution": "HD",
			"mid-resolution": "MD",
			"low-resolution": "SD"
		}, h = typeof document < "u" && document.pictureInPictureEnabled, g, _ = pr("wrapperEl"), v = pr("containerEl"), { width: y } = ns(_), b = is({ interval: 1e3 }), x = /* @__PURE__ */ V(t.autostart ?? !1), S = /* @__PURE__ */ V(!1), ee = /* @__PURE__ */ V(!1), C = /* @__PURE__ */ V(t.mode ?? "auto"), w = /* @__PURE__ */ V(t.poster), T = /* @__PURE__ */ V(0), E = /* @__PURE__ */ V(!1), te = /* @__PURE__ */ V(!1), D = /* @__PURE__ */ V(!1), ne = Y(() => t.attributes.ptz ?? []), O = Y(() => u.value > 0), k = Y(() => y.value === 0 || y.value >= 300), A = Y(() => y.value === 0 || y.value >= 260), re = Y(() => y.value === 0 || y.value >= 200), ie = Y(() => y.value >= 340), j = Y(() => x.value && !O.value && i.value !== "error"), M = Y(() => x.value && O.value), ae = Y(() => D.value ? "opacity-100" : "opacity-0 pointer-events-none"), oe = Y(() => Math.max(2, t.snapshotInterval ?? 10) * 1e3), se = Y(() => (t.attributes.sources ?? []).map((e) => e.role).filter((e) => !!e).filter((e) => e in m)), N = Y(() => C.value === "auto" ? "AUTO" : o.value === "mse" ? "MSE" : "WebRTC"), P = Y(() => {
			if (x.value || !T.value) return "";
			let e = Math.max(0, Math.floor((b.value - T.value) / 1e3));
			if (e < 1) return t.lang?.startsWith("de") ? "Jetzt" : "now";
			if (e < 60) return `${e}s`;
			let n = Math.floor(e / 60);
			return n < 60 ? `${n}m` : `${Math.floor(n / 60)}h`;
		});
		async function ce() {
			let e = n?.value, r = t.attributes.entry_id, i = t.attributes.camera_name;
			if (!e || !r || !i) return;
			E.value = !0;
			let a = `/api/cameraui/snapshot/${r}/${encodeURIComponent(i)}?t=${Date.now()}`;
			try {
				let t = await e.callWS({
					type: "auth/sign_path",
					path: a,
					expires: 60
				});
				w.value = e.hassUrl(t.path);
			} catch {
				E.value = !1;
			}
		}
		let F = Go(ce, oe, { immediate: !1 }), { start: le, stop: ue } = Ko(() => D.value = !1, 3e3, { immediate: !1 });
		function de() {
			D.value = !0, le();
		}
		function fe(e) {
			e.pointerType === "mouse" && (ue(), D.value = !1);
		}
		function pe() {
			T.value = Date.now(), E.value = !1;
		}
		function I() {
			w.value = void 0, T.value = 0, E.value = !1;
		}
		function me() {
			x.value = !0;
		}
		function he() {
			x.value = !x.value;
		}
		async function ge() {
			if (document.fullscreenElement) {
				await document.exitFullscreen();
				return;
			}
			let e = r.videoElement.value;
			e ? (e.controls = !0, await e.requestFullscreen().catch(() => e.controls = !1)) : await _.value?.requestFullscreen();
		}
		function L() {
			let e = se.value;
			if (e.length < 2) return;
			let t = e[(e.indexOf(s.value) + 1) % e.length];
			r.setResolution(t);
		}
		function _e() {
			let e = [
				"auto",
				"webrtc",
				"mse"
			], t = e[(e.indexOf(C.value) + 1) % e.length];
			C.value = t, r.setMode(t);
		}
		function ve() {
			r.setMuted(!c.value);
		}
		function ye() {
			te.value && (te.value = !1, g?.getTracks().forEach((e) => e.stop()), g = void 0, r.setMicrophone(null));
		}
		async function be() {
			if (te.value) {
				ye();
				return;
			}
			if (f.value) try {
				g = await navigator.mediaDevices.getUserMedia({ audio: !0 }), await r.setMicrophone(g.getAudioTracks()[0] ?? null), te.value = !0;
			} catch {
				g?.getTracks().forEach((e) => e.stop()), g = void 0;
			}
		}
		function xe() {
			if (S.value = !!document.fullscreenElement, !document.fullscreenElement) {
				let e = r.videoElement.value;
				e && (e.controls = !1);
			}
		}
		return rr(() => {
			r.containerElement.value = v.value ?? void 0;
		}), G(x, (e) => {
			e ? (r.start(), F.pause()) : (ye(), r.stop(), T.value = 0, ce(), F.resume());
		}, { immediate: !0 }), Zo(document, "fullscreenchange", xe), Ar(ye), (t, n) => (K(), q("div", {
			ref_key: "wrapperEl",
			ref: _,
			class: "cui-player group relative aspect-video w-full overflow-hidden bg-black",
			onPointermove: de,
			onPointerdown: de,
			onPointerleave: fe
		}, [
			J("div", {
				ref_key: "containerEl",
				ref: v,
				class: "absolute inset-0"
			}, null, 512),
			(!U(x) || !U(O)) && U(w) ? (K(), q("img", {
				key: 0,
				class: "absolute inset-0 h-full w-full object-cover",
				src: U(w),
				alt: "",
				onLoad: pe,
				onError: I
			}, null, 40, Lu)) : _a("", !0),
			(!U(x) || !U(O)) && !U(w) ? (K(), q("div", Ru, [J("img", {
				src: U(Hl),
				class: "h-1/3 max-h-20 w-auto opacity-20",
				alt: ""
			}, null, 8, zu)])) : _a("", !0),
			U(x) ? _a("", !0) : (K(), q("button", {
				key: 2,
				type: "button",
				class: "group/tap absolute inset-0 flex cursor-pointer items-center justify-center bg-transparent transition-colors hover:bg-black/20",
				"aria-label": `Go live: ${e.title ?? ""}`,
				onClick: me
			}, [J("span", Vu, [fa(U(lu), { class: "h-7 w-7" })])], 8, Bu)),
			J("div", Hu, [U(E) && !U(T) && !U(x) ? (K(), q("span", Uu, [fa(nu, { size: 14 })])) : U(P) ? (K(), q("span", Wu, ze(U(P)), 1)) : _a("", !0)]),
			U(j) ? (K(), q("div", Gu, [fa(nu, { size: 30 })])) : U(x) && U(i) === "error" ? (K(), q("div", Ku, [fa(U(vu), { class: "h-10 w-10" }), J("span", qu, ze(U(d)?.message || "Stream unavailable"), 1)])) : _a("", !0),
			J("div", { class: Me(["pointer-events-none absolute inset-x-0 top-0 flex items-center gap-2 bg-gradient-to-b from-black/55 to-transparent px-3 py-2.5 pr-28 text-sm font-medium text-white transition-opacity", U(ae)]) }, [U(M) ? (K(), q("span", {
				key: 0,
				class: Me(["inline-flex h-2 w-2 flex-none rounded-full bg-[#f5222d]", { "animate-pulse !bg-[#ff9800]": U(a) }])
			}, null, 2)) : _a("", !0), e.title ? (K(), q("span", Ju, ze(e.title), 1)) : _a("", !0)], 2),
			U(x) && U(k) ? (K(), q("div", {
				key: 5,
				class: Me(["absolute right-2 top-2 z-10 flex items-center gap-1 transition-opacity", U(ae)])
			}, [U(se).length > 1 ? (K(), q("button", {
				key: 0,
				class: Me($u),
				onClick: L
			}, ze(m[U(s)] ?? U(s)), 1)) : _a("", !0), J("button", {
				class: Me($u),
				onClick: _e
			}, ze(U(N)), 1)], 2)) : _a("", !0),
			U(x) ? (K(), q("div", {
				key: 6,
				class: Me(["absolute inset-x-0 bottom-0 flex items-center gap-0.5 bg-gradient-to-t from-black/70 via-black/40 to-transparent px-2 pb-2 pt-8 text-white transition-opacity", U(ae)])
			}, [
				J("button", {
					class: Me(Qu),
					title: "Pause",
					onClick: he
				}, [fa(U(ou), { class: "h-[18px] w-[18px]" })]),
				n[2] ||= J("span", { class: "flex-1" }, null, -1),
				U(ne).length && U(O) && U(ie) ? (K(), q("button", {
					key: 0,
					class: Me([Qu, U(ee) && "bg-white/20"]),
					title: "PTZ",
					onClick: n[0] ||= (e) => ee.value = !U(ee)
				}, [fa(U(Au), { class: "h-[18px] w-[18px]" })], 2)) : _a("", !0),
				U(p) && U(re) ? (K(), q("button", {
					key: 1,
					class: Me(Qu),
					title: U(c) ? "Unmute" : "Mute",
					onClick: ve
				}, [U(c) ? (K(), sa(U(Du), {
					key: 0,
					class: "h-[18px] w-[18px]"
				})) : (K(), sa(U(wu), {
					key: 1,
					class: "h-[18px] w-[18px]"
				}))], 8, Yu)) : _a("", !0),
				U(f) && U(re) ? (K(), q("button", {
					key: 2,
					class: Me([Qu, U(te) && "bg-white/20"]),
					title: U(te) ? "Stop talking" : "Talk",
					onClick: be
				}, [fa(U(xu), { class: "h-[18px] w-[18px]" })], 10, Xu)) : _a("", !0),
				U(h) && U(A) ? (K(), q("button", {
					key: 3,
					disabled: !U(O),
					class: Me(Qu),
					onClick: n[1] ||= (e) => U(r).togglePip()
				}, [U(l) ? (K(), sa(U(fu), {
					key: 0,
					class: "h-[18px] w-[18px]"
				})) : (K(), sa(U(hu), {
					key: 1,
					class: "h-[18px] w-[18px]"
				}))], 8, Zu)) : _a("", !0),
				J("button", {
					class: Me(Qu),
					onClick: ge
				}, [U(S) ? (K(), sa(U(Nu), {
					key: 0,
					class: "h-[18px] w-[18px]"
				})) : (K(), sa(U(Iu), {
					key: 1,
					class: "h-[18px] w-[18px]"
				}))])
			], 2)) : _a("", !0),
			e.entity && U(ne).length && U(O) && U(ee) && U(ie) ? (K(), sa(tu, {
				key: 7,
				entity: e.entity,
				caps: U(ne)
			}, null, 8, ["entity", "caps"])) : _a("", !0)
		], 544));
	}
}), td = {
	viewBox: "0 0 24 24",
	width: "1.2em",
	height: "1.2em"
};
function nd(e, t) {
	return K(), q("svg", td, [...t[0] ||= [J("path", {
		fill: "currentColor",
		d: "M11 15h2v2h-2zm0-8h2v6h-2zm1-5C6.47 2 2 6.5 2 12a10 10 0 0 0 10 10a10 10 0 0 0 10-10A10 10 0 0 0 12 2m0 18a8 8 0 0 1-8-8a8 8 0 0 1 8-8a8 8 0 0 1 8 8a8 8 0 0 1-8 8"
	}, null, -1)]]);
}
var rd = fn({
	name: "mdi-alert-circle-outline",
	render: nd
}), id = { class: "overflow-hidden" }, ad = {
	key: 1,
	class: "flex items-center gap-2 p-4 text-[color:var(--error-color,#db4437)]"
}, od = /* @__PURE__ */ dr({
	__name: "CameraUiCard",
	setup(e) {
		let t = er(Ul), n = er(Wl), r = Y(() => {
			let e = n.value?.entity;
			return e ? t.value?.states[e] : void 0;
		}), i = Y(() => r.value?.attributes ?? {}), a = Y(() => n.value?.entity ? r.value ? !i.value.camera_name || !i.value.entry_id || !i.value.sources?.length ? "Not a camera.ui camera entity" : "" : `Entity not found: ${n.value.entity}` : "No entity configured"), o = Y(() => n.value?.title ?? i.value.friendly_name ?? i.value.camera_name), s = Y(() => i.value.entity_picture);
		return (e, r) => (K(), q("ha-card", id, [U(a) ? (K(), q("div", ad, [fa(U(rd), { class: "h-5 w-5 shrink-0" }), J("span", null, ze(U(a)), 1)])) : (K(), sa(ed, {
			key: 0,
			attributes: U(i),
			entity: U(n)?.entity,
			poster: U(s),
			title: U(o),
			source: U(n)?.source,
			mode: U(n)?.mode,
			autostart: U(n)?.autostart,
			"snapshot-interval": U(n)?.snapshot_interval,
			lang: U(t)?.language
		}, null, 8, [
			"attributes",
			"entity",
			"poster",
			"title",
			"source",
			"mode",
			"autostart",
			"snapshot-interval",
			"lang"
		]))]));
	}
}), sd = { class: "overflow-hidden" }, cd = {
	key: 0,
	class: "p-4 text-[color:var(--secondary-text-color,#727272)]"
}, ld = /* @__PURE__ */ dr({
	__name: "GridCard",
	setup(e) {
		let t = er(Ul), n = er(Gl), r = Y(() => {
			let e = t?.value;
			return (n?.value?.cameras ?? []).map((t) => {
				let n = e?.states[t];
				if (!n) return;
				let r = n.attributes;
				return {
					entity: t,
					attributes: r,
					title: r.friendly_name ?? r.camera_name ?? t
				};
			}).filter((e) => e !== void 0);
		}), i = Y(() => {
			let e = n?.value?.columns;
			if (e && e > 0) return e;
			let t = r.value.length;
			return t <= 1 ? 1 : t <= 4 ? 2 : 3;
		});
		return (e, a) => (K(), q("ha-card", sd, [U(r).length ? (K(), q("div", {
			key: 1,
			class: "grid gap-px bg-black",
			style: De({ gridTemplateColumns: `repeat(${U(i)}, minmax(0, 1fr))` })
		}, [(K(!0), q(Zi, null, Lr(U(r), (e) => (K(), sa(ed, {
			key: e.entity,
			attributes: e.attributes,
			entity: e.entity,
			title: e.title,
			source: U(n)?.source,
			mode: U(n)?.mode,
			autostart: U(n)?.autostart,
			lang: U(t)?.language
		}, null, 8, [
			"attributes",
			"entity",
			"title",
			"source",
			"mode",
			"autostart",
			"lang"
		]))), 128))], 4)) : (K(), q("div", cd, "No cameras configured"))]));
	}
}), ud = "/*! tailwindcss v4.3.3 | MIT License | https://tailwindcss.com */\n@layer properties{@supports (((-webkit-hyphens:none)) and (not (margin-trim:inline))) or ((-moz-orient:inline) and (not (color:rgb(from red r g b)))){*,:before,:after{--tw-rotate-x:initial;--tw-rotate-y:initial;--tw-rotate-z:initial;--tw-skew-x:initial;--tw-skew-y:initial;--tw-gradient-position:initial;--tw-gradient-from:#0000;--tw-gradient-via:#0000;--tw-gradient-to:#0000;--tw-gradient-stops:initial;--tw-gradient-via-stops:initial;--tw-gradient-from-position:0%;--tw-gradient-via-position:50%;--tw-gradient-to-position:100%;--tw-font-weight:initial;--tw-shadow:0 0 #0000;--tw-shadow-color:initial;--tw-shadow-alpha:100%;--tw-inset-shadow:0 0 #0000;--tw-inset-shadow-color:initial;--tw-inset-shadow-alpha:100%;--tw-ring-color:initial;--tw-ring-shadow:0 0 #0000;--tw-inset-ring-color:initial;--tw-inset-ring-shadow:0 0 #0000;--tw-ring-inset:initial;--tw-ring-offset-width:0px;--tw-ring-offset-color:#fff;--tw-ring-offset-shadow:0 0 #0000;--tw-scale-x:1;--tw-scale-y:1;--tw-scale-z:1}::backdrop{--tw-rotate-x:initial;--tw-rotate-y:initial;--tw-rotate-z:initial;--tw-skew-x:initial;--tw-skew-y:initial;--tw-gradient-position:initial;--tw-gradient-from:#0000;--tw-gradient-via:#0000;--tw-gradient-to:#0000;--tw-gradient-stops:initial;--tw-gradient-via-stops:initial;--tw-gradient-from-position:0%;--tw-gradient-via-position:50%;--tw-gradient-to-position:100%;--tw-font-weight:initial;--tw-shadow:0 0 #0000;--tw-shadow-color:initial;--tw-shadow-alpha:100%;--tw-inset-shadow:0 0 #0000;--tw-inset-shadow-color:initial;--tw-inset-shadow-alpha:100%;--tw-ring-color:initial;--tw-ring-shadow:0 0 #0000;--tw-inset-ring-color:initial;--tw-inset-ring-shadow:0 0 #0000;--tw-ring-inset:initial;--tw-ring-offset-width:0px;--tw-ring-offset-color:#fff;--tw-ring-offset-shadow:0 0 #0000;--tw-scale-x:1;--tw-scale-y:1;--tw-scale-z:1}}}@layer theme{:root,:host{--font-sans:var(--paper-font-common-base_-_font-family,Roboto, sans-serif);--font-mono:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace;--color-black:#000;--color-white:#fff;--spacing:.25rem;--text-xs:.75rem;--text-xs--line-height:calc(1 / .75);--text-sm:.875rem;--text-sm--line-height:calc(1.25 / .875);--font-weight-medium:500;--font-weight-semibold:600;--radius-md:.375rem;--animate-pulse:pulse 2s cubic-bezier(.4, 0, .6, 1) infinite;--aspect-video:16 / 9;--default-transition-duration:.15s;--default-transition-timing-function:cubic-bezier(.4, 0, .2, 1);--default-font-family:var(--font-sans);--default-mono-font-family:var(--font-mono);--color-cui-primary:#df2a4c}}@layer base{*,:after,:before{box-sizing:border-box;border:0 solid;margin:0;padding:0}::backdrop{box-sizing:border-box;border:0 solid;margin:0;padding:0}::file-selector-button{box-sizing:border-box;border:0 solid;margin:0;padding:0}html,:host{-webkit-text-size-adjust:100%;tab-size:4;line-height:1.5;font-family:var(--default-font-family,-apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", \"Noto Sans\", Arial, sans-serif, \"Apple Color Emoji\", \"Segoe UI Emoji\", \"Segoe UI Symbol\", \"Noto Color Emoji\");font-feature-settings:var(--default-font-feature-settings,normal);font-variation-settings:var(--default-font-variation-settings,normal);-webkit-tap-highlight-color:transparent}hr{height:0;color:inherit;border-top-width:1px}abbr:where([title]){-webkit-text-decoration:underline dotted;text-decoration:underline dotted}h1,h2,h3,h4,h5,h6{font-size:inherit;font-weight:inherit}a{color:inherit;-webkit-text-decoration:inherit;-webkit-text-decoration:inherit;-webkit-text-decoration:inherit;-webkit-text-decoration:inherit;text-decoration:inherit}b,strong{font-weight:bolder}code,kbd,samp,pre{font-family:var(--default-mono-font-family,ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace);font-feature-settings:var(--default-mono-font-feature-settings,normal);font-variation-settings:var(--default-mono-font-variation-settings,normal);font-size:1em}small{font-size:80%}sub,sup{vertical-align:baseline;font-size:75%;line-height:0;position:relative}sub{bottom:-.25em}sup{top:-.5em}table{text-indent:0;border-color:inherit;border-collapse:collapse}:-moz-focusring:where(:not(iframe)){outline:auto}progress{vertical-align:baseline}summary{display:list-item}ol,ul,menu{list-style:none}img,svg,video,canvas,audio,iframe,embed,object{vertical-align:middle;display:block}img,video{max-width:100%;height:auto}button,input,select,optgroup,textarea{font:inherit;font-feature-settings:inherit;font-variation-settings:inherit;letter-spacing:inherit;color:inherit;opacity:1;background-color:#0000;border-radius:0}::file-selector-button{font:inherit;font-feature-settings:inherit;font-variation-settings:inherit;letter-spacing:inherit;color:inherit;opacity:1;background-color:#0000;border-radius:0}:where(select:is([multiple],[size])) optgroup{font-weight:bolder}:where(select:is([multiple],[size])) optgroup option{padding-inline-start:20px}::file-selector-button{margin-inline-end:4px}::placeholder{opacity:1}@supports (not ((-webkit-appearance:-apple-pay-button))) or (contain-intrinsic-size:1px){::placeholder{color:currentColor}@supports (color:color-mix(in lab, red, red)){::placeholder{color:color-mix(in oklab, currentcolor 50%, transparent)}}}textarea{resize:vertical}::-webkit-search-decoration{-webkit-appearance:none}::-webkit-date-and-time-value{min-height:1lh;text-align:inherit}::-webkit-datetime-edit{display:inline-flex}::-webkit-datetime-edit-fields-wrapper{padding:0}::-webkit-datetime-edit{padding-block:0}::-webkit-datetime-edit-year-field{padding-block:0}::-webkit-datetime-edit-month-field{padding-block:0}::-webkit-datetime-edit-day-field{padding-block:0}::-webkit-datetime-edit-hour-field{padding-block:0}::-webkit-datetime-edit-minute-field{padding-block:0}::-webkit-datetime-edit-second-field{padding-block:0}::-webkit-datetime-edit-millisecond-field{padding-block:0}::-webkit-datetime-edit-meridiem-field{padding-block:0}::-webkit-calendar-picker-indicator{line-height:1}:-moz-ui-invalid{box-shadow:none}button,input:where([type=button],[type=reset],[type=submit]){appearance:button}::file-selector-button{appearance:button}::-webkit-inner-spin-button{height:auto}::-webkit-outer-spin-button{height:auto}[hidden]:where(:not([hidden=until-found])){display:none!important}}@layer components;@layer utilities{.pointer-events-auto{pointer-events:auto}.pointer-events-none{pointer-events:none}.absolute{position:absolute}.relative{position:relative}.static{position:static}.inset-0{inset:0}.inset-x-0{inset-inline:0}.top-0{top:0}.top-1\\.5{top:calc(var(--spacing) * 1.5)}.top-2{top:calc(var(--spacing) * 2)}.right-2{right:calc(var(--spacing) * 2)}.right-3{right:calc(var(--spacing) * 3)}.bottom-0{bottom:0}.bottom-1\\.5{bottom:calc(var(--spacing) * 1.5)}.bottom-2\\.5{bottom:calc(var(--spacing) * 2.5)}.bottom-16{bottom:calc(var(--spacing) * 16)}.left-2\\.5{left:calc(var(--spacing) * 2.5)}.left-3{left:calc(var(--spacing) * 3)}.z-10{z-index:10}.z-20{z-index:20}.flex{display:flex}.grid{display:grid}.inline-flex{display:inline-flex}.aspect-video{aspect-ratio:var(--aspect-video)}.h-1\\/3{height:33.3333%}.h-2{height:calc(var(--spacing) * 2)}.h-5{height:calc(var(--spacing) * 5)}.h-6{height:calc(var(--spacing) * 6)}.h-7{height:calc(var(--spacing) * 7)}.h-9{height:calc(var(--spacing) * 9)}.h-10{height:calc(var(--spacing) * 10)}.h-14{height:calc(var(--spacing) * 14)}.h-24{height:calc(var(--spacing) * 24)}.h-28{height:calc(var(--spacing) * 28)}.h-\\[18px\\]{height:18px}.h-full{height:100%}.max-h-20{max-height:calc(var(--spacing) * 20)}.w-2{width:calc(var(--spacing) * 2)}.w-5{width:calc(var(--spacing) * 5)}.w-6{width:calc(var(--spacing) * 6)}.w-7{width:calc(var(--spacing) * 7)}.w-9{width:calc(var(--spacing) * 9)}.w-10{width:calc(var(--spacing) * 10)}.w-14{width:calc(var(--spacing) * 14)}.w-24{width:calc(var(--spacing) * 24)}.w-\\[18px\\]{width:18px}.w-auto{width:auto}.w-full{width:100%}.flex-1{flex:1}.flex-none{flex:none}.shrink-0{flex-shrink:0}.transform{transform:var(--tw-rotate-x,) var(--tw-rotate-y,) var(--tw-rotate-z,) var(--tw-skew-x,) var(--tw-skew-y,)}.animate-pulse{animation:var(--animate-pulse)}.cursor-pointer{cursor:pointer}.flex-col{flex-direction:column}.items-center{align-items:center}.justify-center{justify-content:center}.gap-0\\.5{gap:calc(var(--spacing) * .5)}.gap-1{gap:var(--spacing)}.gap-2{gap:calc(var(--spacing) * 2)}.gap-px{gap:1px}.overflow-hidden{overflow:hidden}.rounded-\\[10px\\]{border-radius:10px}.rounded-full{border-radius:2147483647px}.rounded-md{border-radius:var(--radius-md)}.\\!bg-\\[\\#ff9800\\]{background-color:#ff9800!important}.bg-\\[\\#f5222d\\]{background-color:#f5222d}.bg-black{background-color:var(--color-black)}.bg-black\\/40{background-color:#0006}@supports (color:color-mix(in lab, red, red)){.bg-black\\/40{background-color:color-mix(in oklab, var(--color-black) 40%, transparent)}}.bg-black\\/45{background-color:#00000073}@supports (color:color-mix(in lab, red, red)){.bg-black\\/45{background-color:color-mix(in oklab, var(--color-black) 45%, transparent)}}.bg-black\\/50{background-color:#00000080}@supports (color:color-mix(in lab, red, red)){.bg-black\\/50{background-color:color-mix(in oklab, var(--color-black) 50%, transparent)}}.bg-transparent{background-color:#0000}.bg-white\\/20{background-color:#fff3}@supports (color:color-mix(in lab, red, red)){.bg-white\\/20{background-color:color-mix(in oklab, var(--color-white) 20%, transparent)}}.bg-gradient-to-b{--tw-gradient-position:to bottom in oklab;background-image:linear-gradient(var(--tw-gradient-stops))}.bg-gradient-to-t{--tw-gradient-position:to top in oklab;background-image:linear-gradient(var(--tw-gradient-stops))}.from-black\\/55{--tw-gradient-from:#0000008c}@supports (color:color-mix(in lab, red, red)){.from-black\\/55{--tw-gradient-from:color-mix(in oklab, var(--color-black) 55%, transparent)}}.from-black\\/55{--tw-gradient-stops:var(--tw-gradient-via-stops,var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position))}.from-black\\/70{--tw-gradient-from:#000000b3}@supports (color:color-mix(in lab, red, red)){.from-black\\/70{--tw-gradient-from:color-mix(in oklab, var(--color-black) 70%, transparent)}}.from-black\\/70{--tw-gradient-stops:var(--tw-gradient-via-stops,var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position))}.via-black\\/40{--tw-gradient-via:#0006}@supports (color:color-mix(in lab, red, red)){.via-black\\/40{--tw-gradient-via:color-mix(in oklab, var(--color-black) 40%, transparent)}}.via-black\\/40{--tw-gradient-via-stops:var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-via) var(--tw-gradient-via-position), var(--tw-gradient-to) var(--tw-gradient-to-position);--tw-gradient-stops:var(--tw-gradient-via-stops)}.to-transparent{--tw-gradient-to:transparent;--tw-gradient-stops:var(--tw-gradient-via-stops,var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position))}.object-cover{object-fit:cover}.p-4{padding:calc(var(--spacing) * 4)}.px-2{padding-inline:calc(var(--spacing) * 2)}.px-3{padding-inline:calc(var(--spacing) * 3)}.px-4{padding-inline:calc(var(--spacing) * 4)}.py-0\\.5{padding-block:calc(var(--spacing) * .5)}.py-2\\.5{padding-block:calc(var(--spacing) * 2.5)}.pt-8{padding-top:calc(var(--spacing) * 8)}.pr-28{padding-right:calc(var(--spacing) * 28)}.pb-2{padding-bottom:calc(var(--spacing) * 2)}.pl-1{padding-left:var(--spacing)}.text-center{text-align:center}.text-sm{font-size:var(--text-sm);line-height:var(--tw-leading,var(--text-sm--line-height))}.text-xs{font-size:var(--text-xs);line-height:var(--tw-leading,var(--text-xs--line-height))}.text-\\[11px\\]{font-size:11px}.font-medium{--tw-font-weight:var(--font-weight-medium);font-weight:var(--font-weight-medium)}.font-semibold{--tw-font-weight:var(--font-weight-semibold);font-weight:var(--font-weight-semibold)}.text-ellipsis{text-overflow:ellipsis}.whitespace-nowrap{white-space:nowrap}.text-\\[color\\:var\\(--error-color\\,\\#db4437\\)\\]{color:var(--error-color,#db4437)}.text-\\[color\\:var\\(--secondary-text-color\\,\\#727272\\)\\]{color:var(--secondary-text-color,#727272)}.text-white{color:var(--color-white)}.text-white\\/60{color:#fff9}@supports (color:color-mix(in lab, red, red)){.text-white\\/60{color:color-mix(in oklab, var(--color-white) 60%, transparent)}}.opacity-0{opacity:0}.opacity-20{opacity:.2}.opacity-100{opacity:1}.shadow{--tw-shadow:0 1px 3px 0 var(--tw-shadow-color,#0000001a), 0 1px 2px -1px var(--tw-shadow-color,#0000001a);box-shadow:var(--tw-inset-shadow), var(--tw-inset-ring-shadow), var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow)}.transition{transition-property:color,background-color,border-color,outline-color,text-decoration-color,fill,stroke,--tw-gradient-from,--tw-gradient-via,--tw-gradient-to,opacity,box-shadow,transform,translate,scale,rotate,filter,-webkit-backdrop-filter,backdrop-filter,display,content-visibility,overlay,pointer-events;transition-timing-function:var(--tw-ease,var(--default-transition-timing-function));transition-duration:var(--tw-duration,var(--default-transition-duration))}.transition-colors{transition-property:color,background-color,border-color,outline-color,text-decoration-color,fill,stroke,--tw-gradient-from,--tw-gradient-via,--tw-gradient-to;transition-timing-function:var(--tw-ease,var(--default-transition-timing-function));transition-duration:var(--tw-duration,var(--default-transition-duration))}.transition-opacity{transition-property:opacity;transition-timing-function:var(--tw-ease,var(--default-transition-timing-function));transition-duration:var(--tw-duration,var(--default-transition-duration))}@media (hover:hover){.group-hover\\/tap\\:scale-105:is(:where(.group\\/tap):hover *){--tw-scale-x:105%;--tw-scale-y:105%;--tw-scale-z:105%;scale:var(--tw-scale-x) var(--tw-scale-y)}.hover\\:bg-black\\/20:hover{background-color:#0003}@supports (color:color-mix(in lab, red, red)){.hover\\:bg-black\\/20:hover{background-color:color-mix(in oklab, var(--color-black) 20%, transparent)}}.hover\\:bg-black\\/60:hover{background-color:#0009}@supports (color:color-mix(in lab, red, red)){.hover\\:bg-black\\/60:hover{background-color:color-mix(in oklab, var(--color-black) 60%, transparent)}}.hover\\:bg-white\\/15:hover{background-color:#ffffff26}@supports (color:color-mix(in lab, red, red)){.hover\\:bg-white\\/15:hover{background-color:color-mix(in oklab, var(--color-white) 15%, transparent)}}}.disabled\\:cursor-default:disabled{cursor:default}.disabled\\:opacity-40:disabled{opacity:.4}}.cui-video{object-fit:cover!important}.cui-video:fullscreen{object-fit:contain!important}@keyframes cui-spin-rotate{to{transform:rotate(360deg)}}@keyframes cui-spin-dash{0%{stroke-dasharray:1 200;stroke-dashoffset:0}50%{stroke-dasharray:89 200;stroke-dashoffset:-35px}to{stroke-dasharray:89 200;stroke-dashoffset:-124px}}.cui-spin{transform-origin:50%;animation:2s linear infinite cui-spin-rotate}.cui-spin-circle{stroke:var(--color-cui-primary,#df2a4c);stroke-linecap:round;animation:1.5s ease-in-out infinite cui-spin-dash}.cui-ptz-pad,.cui-ptz-track{touch-action:none;cursor:grab;background:#0000008c;border-radius:9999px;box-shadow:inset 0 0 0 1px #ffffff1f}.cui-ptz-pad:active,.cui-ptz-track:active{cursor:grabbing}.cui-ptz-knob{pointer-events:none;background:#fff;border-radius:9999px;justify-content:center;align-items:center;width:1.625rem;height:1.625rem;display:flex;position:absolute;top:50%;left:50%;box-shadow:0 2px 6px #00000059}.cui-ptz-knob-icon{color:#00000059;width:.85rem;height:.85rem}.cui-ptz-mark{color:#ffffff8c;pointer-events:none;font-size:.8rem;line-height:1;position:absolute;left:50%;transform:translate(-50%)}@property --tw-rotate-x{syntax:\"*\";inherits:false}@property --tw-rotate-y{syntax:\"*\";inherits:false}@property --tw-rotate-z{syntax:\"*\";inherits:false}@property --tw-skew-x{syntax:\"*\";inherits:false}@property --tw-skew-y{syntax:\"*\";inherits:false}@property --tw-gradient-position{syntax:\"*\";inherits:false}@property --tw-gradient-from{syntax:\"<color>\";inherits:false;initial-value:#0000}@property --tw-gradient-via{syntax:\"<color>\";inherits:false;initial-value:#0000}@property --tw-gradient-to{syntax:\"<color>\";inherits:false;initial-value:#0000}@property --tw-gradient-stops{syntax:\"*\";inherits:false}@property --tw-gradient-via-stops{syntax:\"*\";inherits:false}@property --tw-gradient-from-position{syntax:\"<length-percentage>\";inherits:false;initial-value:0%}@property --tw-gradient-via-position{syntax:\"<length-percentage>\";inherits:false;initial-value:50%}@property --tw-gradient-to-position{syntax:\"<length-percentage>\";inherits:false;initial-value:100%}@property --tw-font-weight{syntax:\"*\";inherits:false}@property --tw-shadow{syntax:\"*\";inherits:false;initial-value:0 0 #0000}@property --tw-shadow-color{syntax:\"*\";inherits:false}@property --tw-shadow-alpha{syntax:\"<percentage>\";inherits:false;initial-value:100%}@property --tw-inset-shadow{syntax:\"*\";inherits:false;initial-value:0 0 #0000}@property --tw-inset-shadow-color{syntax:\"*\";inherits:false}@property --tw-inset-shadow-alpha{syntax:\"<percentage>\";inherits:false;initial-value:100%}@property --tw-ring-color{syntax:\"*\";inherits:false}@property --tw-ring-shadow{syntax:\"*\";inherits:false;initial-value:0 0 #0000}@property --tw-inset-ring-color{syntax:\"*\";inherits:false}@property --tw-inset-ring-shadow{syntax:\"*\";inherits:false;initial-value:0 0 #0000}@property --tw-ring-inset{syntax:\"*\";inherits:false}@property --tw-ring-offset-width{syntax:\"<length>\";inherits:false;initial-value:0}@property --tw-ring-offset-color{syntax:\"*\";inherits:false;initial-value:#fff}@property --tw-ring-offset-shadow{syntax:\"*\";inherits:false;initial-value:0 0 #0000}@property --tw-scale-x{syntax:\"*\";inherits:false;initial-value:1}@property --tw-scale-y{syntax:\"*\";inherits:false;initial-value:1}@property --tw-scale-z{syntax:\"*\";inherits:false;initial-value:1}@keyframes pulse{50%{opacity:.5}}", dd = {
	"/api/go2rtc": "go2rtc",
	"/api/proxy": "rpc"
}, fd = 4e3, pd = 4002;
function md(e) {
	let t = {
		id: "ha-ws",
		kind: "per-resource",
		phaseGating: !1
	}, n = /* @__PURE__ */ new Set(), r = !1;
	function i(e, t, n) {
		for (let r of [...e.listeners.close]) r({
			code: t,
			reason: n,
			wasClean: !1
		});
	}
	async function a(t) {
		try {
			let n = e.getHass(), r = e.getEntryId(), i = dd[t.spec.path];
			if (!n || !r || !i) throw Error(`cannot resolve proxy target for ${t.spec.path}`);
			let a = new URLSearchParams();
			for (let [e, n] of Object.entries(t.spec.query ?? {})) n != null && n !== "" && a.set(e, n);
			let o = a.toString(), s = `/api/cameraui/ws/${r}/${i}${o ? `?${o}` : ""}`, c = await n.callWS({
				type: "auth/sign_path",
				path: s
			});
			if (t.disposed) return;
			let l = "ws" + n.hassUrl(c.path).substring(4), u = new WebSocket(l, t.spec.protocols);
			t.spec.binaryType && (u.binaryType = t.spec.binaryType), t.ws = u, t.url = l, u.onopen = () => {
				if (!(t.disposed || t.ws !== u)) for (let e of [...t.listeners.open]) e();
			}, u.onmessage = (e) => {
				if (!(t.disposed || t.ws !== u)) for (let n of [...t.listeners.message]) n(e);
			}, u.onerror = (e) => {
				if (!(t.disposed || t.ws !== u)) for (let n of [...t.listeners.error]) n(e);
			}, u.onclose = (e) => {
				if (t.ws === u) t.ws = null, t.url = null;
				else return;
				for (let n of [...t.listeners.close]) n({
					code: e.code,
					reason: e.reason,
					wasClean: e.wasClean
				});
			};
		} catch (e) {
			t.disposed || i(t, fd, e instanceof Error ? e.message : String(e));
		}
	}
	function o(e, t, n) {
		let r = e.ws;
		if (r) {
			e.ws = null, e.url = null, r.onclose = null, r.onmessage = null, r.onerror = null, r.onopen = null;
			try {
				r.close(t, n);
			} catch {}
			i(e, t, n);
		}
	}
	function s(e) {
		if (r) throw Error("ha-ws-transport disposed");
		let t = {
			spec: e,
			listeners: {
				open: /* @__PURE__ */ new Set(),
				close: /* @__PURE__ */ new Set(),
				message: /* @__PURE__ */ new Set(),
				error: /* @__PURE__ */ new Set()
			},
			ws: null,
			url: null,
			disposed: !1
		};
		return n.add(t), a(t), {
			get readyState() {
				return t.ws?.readyState ?? WebSocket.CLOSED;
			},
			get url() {
				return t.url;
			},
			send(e) {
				if (t.disposed) throw Error("ws-handle disposed");
				let n = t.ws;
				if (!n) throw Error("ws-handle: no active socket");
				if (n.readyState !== WebSocket.OPEN) throw Error("ws-handle: socket not open");
				n.send(e);
			},
			close(e, n) {
				o(t, e ?? 1e3, n ?? "");
			},
			on(e, n) {
				let r = t.listeners[e];
				return r.add(n), () => {
					r.delete(n);
				};
			},
			dispose() {
				if (t.disposed) return;
				t.disposed = !0;
				let e = t.ws;
				if (t.ws = null, t.url = null, e) {
					e.onclose = null, e.onmessage = null, e.onerror = null, e.onopen = null;
					try {
						e.close(pd, "disposed");
					} catch {}
				}
				t.listeners.open.clear(), t.listeners.close.clear(), t.listeners.message.clear(), t.listeners.error.clear(), n.delete(t);
			}
		};
	}
	return {
		get spec() {
			return t;
		},
		get handleCount() {
			return n.size;
		},
		async apply(e) {},
		health() {
			return { up: !0 };
		},
		on() {
			return () => {};
		},
		async dispose() {
			r = !0;
			for (let e of [...n]) e.disposed = !0, o(e, pd, "disposed");
			n.clear();
		},
		open: s
	};
}
//#endregion
//#region src/context.ts
function hd(e) {
	let t = md(e), n = null, r = Y(() => {
		let t = e.getHass();
		return !t || !e.getEntryId() ? null : (n ??= {
			endpoint: {
				url: t.hassUrl("/"),
				mode: "direct-lan"
			},
			tokens: { access: "" }
		}, n);
	});
	return fn({
		rpc: /* @__PURE__ */ H(void 0),
		target: r,
		isConnected: Y(() => r.value !== null),
		endpoint: Y(() => r.value?.endpoint.url),
		token: Y(() => void 0),
		extraProxyQuery: Y(() => void 0),
		error: /* @__PURE__ */ V(void 0),
		wsTransport: t,
		on: () => {},
		off: () => {}
	});
}
//#endregion
//#region src/main.ts
function gd(e, t) {
	for (let n of t) {
		let t = e.value?.states[n]?.attributes?.entry_id;
		if (t) return t;
	}
}
function _d(e, t) {
	if (t.split(".")[0] !== "camera") return !1;
	let n = e?.states[t]?.attributes;
	return !!(n?.entry_id && Array.isArray(n.sources));
}
function vd(e) {
	if (e) return Object.keys(e.states).find((t) => _d(e, t));
}
function yd(e, t, n, r, i, a) {
	let o = e.shadowRoot ?? e.attachShadow({ mode: "open" });
	o.innerHTML = "";
	let s = document.createElement("style");
	s.textContent = ud;
	let c = document.createElement("div");
	o.append(s, c);
	let l = hd({
		getHass: () => n.value,
		getEntryId: a
	}), u = Po(t);
	return u.provide(Ul, n), u.provide(r, i), u.use(Ic(l)), u.mount(c), u;
}
function bd(e, t) {
	t.unmount(), e.shadowRoot && (e.shadowRoot.innerHTML = "");
}
var xd = class extends HTMLElement {
	app = null;
	hassRef = /* @__PURE__ */ H(void 0);
	configRef = /* @__PURE__ */ H(void 0);
	setConfig(e) {
		if (!e?.entity) throw Error("cameraui-card: \"entity\" is required");
		this.configRef.value = e;
	}
	set hass(e) {
		this.hassRef.value = e;
	}
	get hass() {
		return this.hassRef.value;
	}
	getCardSize() {
		return 5;
	}
	getGridOptions() {
		return {
			rows: 4,
			columns: 12,
			min_rows: 3
		};
	}
	static getStubConfig(e) {
		return { entity: vd(e) ?? "" };
	}
	static getConfigForm() {
		return { schema: [
			{
				name: "entity",
				required: !0,
				selector: { entity: { domain: "camera" } }
			},
			{
				name: "title",
				selector: { text: {} }
			},
			{
				type: "grid",
				name: "",
				schema: [{
					name: "autostart",
					selector: { boolean: {} }
				}, {
					name: "snapshot_interval",
					selector: { number: {
						mode: "box",
						min: 0,
						unit_of_measurement: "s"
					} }
				}]
			}
		] };
	}
	connectedCallback() {
		this.app ??= yd(this, od, this.hassRef, Wl, this.configRef, () => gd(this.hassRef, this.configRef.value?.entity ? [this.configRef.value.entity] : []));
	}
	disconnectedCallback() {
		queueMicrotask(() => {
			!this.isConnected && this.app && (bd(this, this.app), this.app = null);
		});
	}
}, Sd = class extends HTMLElement {
	app = null;
	hassRef = /* @__PURE__ */ H(void 0);
	configRef = /* @__PURE__ */ H(void 0);
	setConfig(e) {
		if (!e?.cameras?.length) throw Error("cameraui-grid-card: \"cameras\" is required");
		this.configRef.value = e;
	}
	set hass(e) {
		this.hassRef.value = e;
	}
	get hass() {
		return this.hassRef.value;
	}
	getCardSize() {
		return 6;
	}
	getGridOptions() {
		return {
			rows: 6,
			columns: 12,
			min_rows: 3
		};
	}
	static getStubConfig(e) {
		let t = vd(e);
		return { cameras: t ? [t] : [] };
	}
	static getConfigForm() {
		return { schema: [{
			name: "cameras",
			required: !0,
			selector: { entity: {
				domain: "camera",
				multiple: !0
			} }
		}, {
			name: "columns",
			selector: { number: {
				mode: "box",
				min: 1,
				max: 6
			} }
		}] };
	}
	connectedCallback() {
		this.app ??= yd(this, ld, this.hassRef, Gl, this.configRef, () => gd(this.hassRef, this.configRef.value?.cameras ?? []));
	}
	disconnectedCallback() {
		queueMicrotask(() => {
			!this.isConnected && this.app && (bd(this, this.app), this.app = null);
		});
	}
};
customElements.get("cameraui-card") || customElements.define("cameraui-card", xd), customElements.get("cameraui-grid-card") || customElements.define("cameraui-grid-card", Sd), window.customCards = window.customCards ?? [], window.customCards.push({
	type: "cameraui-card",
	name: "camera.ui Card",
	description: "Live view for camera.ui cameras with WebRTC/MSE, source switching and H.265 support.",
	documentationURL: "https://github.com/cameraui/homeassistant-integration",
	preview: !0,
	getEntitySuggestion: (e, t) => _d(e, t) ? { config: {
		type: "custom:cameraui-card",
		entity: t
	} } : null
}, {
	type: "cameraui-grid-card",
	name: "camera.ui Grid",
	description: "A grid of camera.ui live views, click any tile to go live.",
	documentationURL: "https://github.com/cameraui/homeassistant-integration"
});
//#endregion
