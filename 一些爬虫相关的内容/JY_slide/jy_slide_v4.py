# 处理 selenium 移动滑块时候的卡顿问题
import selenium.webdriver.common.actions.pointer_input as pointer
pointer.PointerInput.DEFAULT_MOVE_DURATION = 20
pointer.PointerInput._bak_create_pointer_move = pointer.PointerInput.create_pointer_move
def create_pointer_move(self, *a, **kw):
    kw['duration'] = 1
    return self._bak_create_pointer_move(*a, **kw)
pointer.PointerInput.create_pointer_move = create_pointer_move

import cv2
import numpy as np
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as wbw

import time
import base64
import random
import threading
from io import BytesIO

def read_from_bytes(bytes_img, size=None):
    image_data = BytesIO(bytes_img)
    img = Image.open(image_data)
    if size:
        img = img.resize(size)
    img = np.asarray(img)
    return img

def read_from_b64string(str_img, size=None):
    image_data = BytesIO(base64.b64decode(str_img.split('base64,', 1)[1]))
    img = Image.open(image_data)
    if size:
        img = img.resize(size)
    img = np.asarray(img)
    return img

def findmatchtemplate_np(front_np, bg_np):
    def canny(v, left=180, right=240):
        s = cv2.cvtColor(v, cv2.COLOR_BGR2GRAY)
        s = cv2.Canny(s, left, right)
        return s
    bg_np = cv2.pyrMeanShiftFiltering(bg_np, 5, 50)
    img1 = canny(front_np)
    img2 = canny(bg_np)
    w, h = img1.shape[:2]
    v = cv2.matchTemplate(img2,img1,cv2.TM_CCOEFF)
    a, b, c, left_top = cv2.minMaxLoc(v)
    def accurate(left_top, canny_img1):
        s = canny_img1
        v = []
        for idx,i in enumerate(s):
            if any(i):
                v.append(idx)
        gt = v[0]
        h = v[-1] - v[0]
        s = s.T
        v = []
        for idx,i in enumerate(s):
            if any(i):
                v.append(idx)
        gl = v[0]
        w = v[-1] - v[0]
        t, l = left_top[1]+gt, left_top[0]+gl
        return t, l, w, h
    t, l, w, h = accurate(left_top, img1)
    def test():
        cv2.imshow('nier1', img1)
        cv2.imshow('nier2', img2)
        img3 = bg_np
        img3 = cv2.rectangle(img3, (l, t), (l+h, t+w), (0,255,0), 2)
        cv2.imshow('nier', img3)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()
    test() # 使用时注释这行就可以了
    return t, l, w, h

def get_driver():
    from selenium import webdriver
    option = webdriver.ChromeOptions()
    extset = ['enable-automation', 'ignore-certificate-errors']
    ignimg = "profile.managed_default_content_settings.images"
    mobile = {'deviceName':'Galaxy S5'}

    # 需要哪些 driver 功能，请解开对应的代码注释再启动
    option.add_argument("--disable-infobars")                       # 关闭调试信息
    option.add_experimental_option("excludeSwitches", extset)       # 关闭调试信息
    option.add_experimental_option("useAutomationExtension", False) # 关闭调试信息
    # option.add_argument('--start-maximized')                        # 最大化
    # option.add_experimental_option('mobileEmulation', mobile)     # 手机模式
    # option.add_experimental_option("prefs", {ignore_image: 2})    # 不加载图片
    # option.add_argument('--headless')                             # 【*】 无界面
    # option.add_argument('--no-sandbox')                           # 【*】 沙箱模式
    # option.add_argument('--disable-dev-shm-usage')                # 【*】 in linux
    # option.add_argument('--window-size=1920,1080')                # 无界面最大化
    # option.add_argument('--disable-gpu')                          # 禁用 gpu 加速
    # option.add_argument("--auto-open-devtools-for-tabs")          # F12
    # option.add_argument("--user-agent=Mozilla/5.0 VILAME")        # 修改 UA
    # option.add_argument('--proxy-server=http://127.0.0.1:8888')   # 代理

    webdriver = webdriver.Chrome(options=option, executable_path='chromedriver')
    webdriver.set_page_load_timeout(5)
    _bak_get = webdriver.get
    def get(url):
        import selenium
        try:
            _bak_get(url)
        except selenium.common.exceptions.TimeoutException:
            print('selenium.common.exceptions.TimeoutException: {}'.format(url))
            get(url)
    webdriver.get = get
    webdriver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": r"""
            // s4q84hc@ArrMK(=(6p(h-(p;vOFKU~G?SNFo`*!#`f&T@Pn8RY&wsXaU_V)jq7YnbWupnYRJRRmUvP?`0K(#(7sM<h1R+$%g)&2hYqsd~b6wBoUId!1oA2?G6pY_9_NTSSL&W2qzRYGnYp3P%kWcfZ;-ah@fn#BNpCDC`>`01+i-*AM-#tT$LzguWE3Uv8=0BJc{SV^K?8Izf8AXzl5`idhqXm#t{`fIMs)oaV?}u7NvD<8+Qmc!t{vmHyW1{``jEQB~KzN?^9$s!7y-s$kS;CBUr<5NHr(HJ1>wRxc?vv%habah;YD`JZUUB9|xtB8xs(W+ff9ePCr5e+KJMn#)!XilA6C&0)HLW)CMh_LO{E4Ed9wa7oZnfq&1~$>u$O&K$WNCsrq*#YHrsYGO1N`(6&nL+6L2E8U=$1R^$~fR|veKPW?>`YwB$$;8NC>?fYX5Oja2$7i0S5X6#_}G+gTh){_F(mG1{mHZa!h0^f_Q`*v1a;P;Sz@pzlTWTY>q}lEooD+tUPs&a<ic#B7zk)v+WLqI0^D}16elZ4V!UB=COoNExtxpr;S&iUh*N!+HbIdMlNo9Bw%;Q)e>PsN;TD^rg~zk=!yJ(T^TcQi>=@kQB|-5l{~Tb#|#8Q5~3oJ!^v(`RT$cs)GMS_<I7Bj(US+#6I<*uI*^2Ag5zYLIp{0D=es%gK1UvDI`qLHnf{1$#X}$S3CI!L9!o19M7ycm2!b%HfZBM4rlFZ%c)64);K=soqt&uR_F3hTXX)9P4w;PsQ_*$@1ek>>pzE$fja;_+aB^^Id1=}*n{RP3+=ebz@1n3QkiCbs@MPRWPiNUC7jFOpb`*vZmK!(Ffj>}{l0EJYr&$Y0FxWB^k2Fe`pvER`E4$|DDr&=suQJNfu!Z3)A~7Gn2botVn&jpWUsi#zvB(jB%LM2wIePeBuNe@SG$5>N*y~>-^aZjRVGX+#3U^5UibG9A
            !function(n,e,t,r,u,i,f,o,c,d,l,a,p,s,m,g,y,h,b,v,w,k,x,O,_,j,C,I,q,R,z,A,E,F,P,S,$,B,D,M,U,G,H,J,K,L,N,Q,T,V,W,X,Y,Z,nn,en,tn,rn,un,fn,on,cn,dn,ln,an,pn,sn,mn,gn,yn,hn,bn,vn,wn,kn,xn,On,_n,jn,Cn,In,qn,Rn,zn,An,En,Fn,Pn,Sn,$n,Bn,Dn,Mn,Un,Gn,Hn,Jn,Kn,Ln,Nn,Qn,Tn,Vn,Wn,Xn,Yn,Zn,ne,ee,te,re,ue,ie,fe,oe,ce,de,le,ae,pe,se,me,ge,ye,he,be,ve,we,ke,xe,Oe,_e,je,Ce,Ie,qe,Re,ze,Ae,Ee,Fe,Pe,Se){function $e(n,e,t,r,i,f,d,s,h,v){return e==oe?(r?t[Mn][nn[dn]]()||t[ge][nn[dn]]():t[Mn][nn[cn]](en)||t[ge][nn[cn]](en))&&undefined:e==ae?(t={})&&(t[Mn]=[])&&(t[ge]=[])&&((t[Rn]=en)||tn)&&t:e==sn?t?r[R(r)-tn]:r[R(r)-tn]=i:e==ee?A(r,Yn)?E(r,Yn):A(r,yn)?E(r,yn):i?K(t,r):E(r,Ln):e==on?((i={})[nn[Zn]]=t)&&i:e==he?t[nn[Dn]]:e==In?!(i=b[t[r]])||r!=Yn&&r!=Ln?i:t[nn[ae]]?j[t[nn[ae]]]:((t[nn[ae]]=t[nn[rn]]+nn[ae]+(t[nn[Pn]]^On))||tn)&&((j[t[nn[ae]]]=F(rn,F(tn,i),t[nn[Pn]]&ze))||tn)&&j[t[nn[ae]]]:e==Un?(f=P(r?t[nn[qn]](r):t))&&[i?null:t[nn[qn]](r+f[tn],r+f[en]+f[tn]),r+f[en]+f[tn]]:e==zn?(I+=tn)&&u:e==Ce?i&&r!=nn[Cn]?q[nn[hn]](t,r):r in t:e==ne?((A(t,Ln)?Z[en][E(t,Ln)]=Z[fn][r]:A(t,An)?Z[en][E(E(t[An],Ln),Ln)]=l(Z[fn])[nn[Hn]](Q)[nn[qn]](r):tn)||tn)&&undefined:e==Vn?Z[fn][t]:e==de?t==tn?F(tn,X(un,r))[en]^i&ze:t==rn?F(rn,F(tn,X(un,r)),i&ze):t==un?c(r[nn[Xn]](O,nn[Un])):undefined:e==be?i==an?X(tn,t,r):i==Ln?X(un,t):i==dn?null:i==Yn?X(un,t):i==yn?a(X(rn,t,r)):i==Dn?!!p(o(X(tn,t,r))):i==en?g(X(rn,t,r)):i==gn?((f=X(rn,t,r))||tn)&&m(f[nn[qn]](en,f[nn[on]](nn[ae])),f[nn[qn]](f[nn[on]](nn[ae])+tn)):en:e==_e?y++&&I++:e==pe?(v=[][nn[vn]](t,[Z=[{},f,i,d,s]]))&&(r!==nn[Yn]?Z[en][r]=h:tn)&&Z[tn][nn[Hn]](N)&&!(n-y)&&K(v,Z[rn],U()):function w(){return T(t,r,i,f,this,arguments,w)}}function Be(n,e,t,r,u,i,f,c,l,a){for(e==qn?i=R(t)-tn:e==Pn?!(f=en)&&(i=R(t)-tn):e==je?(u=nn[Jn])||(i=t):e==hn?!(r=en)&&!(c=en)&&(u=t[nn[xn]](x)[en])&&((i=u[nn[qn]](en,-tn))||tn)&&(f=u[nn[re]](R(u)-tn))&&((r+=w[nn[sn]](f))||tn)&&(l=R(i)-tn):e==xn?(i=[])&&(f=en):e==me?(t=t[nn[xn]](m(x,nn[tn])))&&(r=t[nn[qn]](tn,-tn))&&(u=[])&&r[nn[Hn]](function(n){for(((i=P(n)[en][nn[ln]](bn))||tn)&&!(c=en)&&(f=ln-R(i));c<f;c++)i=nn[ue]+i;u[nn[cn]](i)})&&!(c=en)&&(l=P(t[nn[qn]](-tn)[en])[en][nn[ln]](bn)):e==Nn&&(r=S(t,en))&&((u=r[en])||tn)&&((i=r[tn])||tn)&&((u=V(u))||tn)&&(n[nn[pn]]=$e[nn[In]](tn,n,_e))&&(n[nn[ln]]=$e[nn[In]](tn,n,zn));e==qn||e==Pn?i>=en:e==je?i<r:e==hn?l>=en:e==xn?f<R(r):e==me?c<P(t[nn[qn]](en,tn)[en])[en]-R(r)*ln-R(l):e==Nn?R(u):en;e==qn?i--:e==Pn?f++&&i--:e==je?i++:e==hn?l--:e==xn?f++:e==me?c++:en)if(e==qn?A(t[i][en],r,tn)&&(l=!0)&&((c=t[i][en][r]=u)||tn)&&l:e==Pn?f==en&&((r==nn[Yn]?(l=!0)&&(c=null):r==nn[yn]?(l=!0)&&(c=G(tn,t)[fn]):r==nn[Gn]?(l=!0)&&(c=t[en][dn]):en)||tn)&&l||((i==en&&r==nn[mn]?(l=!0)&&(c=t[en][en]):A(t[i][en],r,tn)?(l=!0)&&(c=t[i][en][r]):en)||tn)&&l||i==en&&((r==nn[wn]?(l=!0)&&(c=u&&typeof exports==nn[Vn]?undefined:exports):r==nn[gn]?(l=!0)&&(c=u&&typeof module==nn[Vn]?undefined:module):r==nn[le]?(l=!0)&&(c=u&&typeof require==nn[Vn]?undefined:require):((c=t[i][en][r])||tn)&&(c||r in t[i][en])&&(l=!0))||tn)&&l:e==je?(u+=o(i))&&en:e==hn?((r+=k[nn[sn]](i[nn[re]](l))*s(R(k),c)*R(w))||tn)&&c++&&en:e==xn?(i[f]=t==tn?r[nn[bn]](f):o(r[f]^u))&&en:e==me?(l=nn[ue]+l)&&en:e==Nn?(l=p(u[nn[qn]](en,tn),bn))&&((a=p(u[nn[qn]](tn,tn+l),bn))||tn)&&(f=tn+l)&&(c=f+a)&&h[nn[cn]](u[nn[qn]](f,c))&&(u=u[nn[qn]](c))&&en:en)return c;if(e==Pn&&!u)throw d(r+nn[Ln]);return e==qn?t[en][en][r]=u:e==je?u:e==hn?[r,R(u)]:e==xn?t==tn?i:i[nn[Nn]](nn[Jn]):e==me?u[nn[cn]](l)&&u[nn[Nn]](nn[Jn]):e==Nn?t[nn[qn]](i):void 0}function K(n,e,t,u,o,c,d,l,a,p,m,g,h,b,v,w,k,x,O,_,j,C,I,q,z,F,P,S,L,N){return(a=t[l=t[nn[rn]]])&&l==In?function(){throw K(e,a[en])}():l==Un?function(){debugger}():l==an||l==Yn||l==yn||l==Dn||l==dn||l==en||l==gn?E(t,l):l==Kn?a[nn[Hn]](function(n){K(e,n)}):l==Vn?A(a[en],Jn)?((q=K(e,a[tn]))||tn)&&a[en][Jn][nn[Hn]](function(n,t){G(tn,e)[en][E(n,Ln)]=q[t]}):(I=E(a[en],Ln))&&((q=K(e,a[tn]))||tn)&&(A(a[tn],an)&&E(a[tn],an)==Oe?G(tn,e)[en][I]=G(tn,e)[en][I]:G(tn,e)[en][I]=q):l==ne?a[nn[Hn]](function(n){K(e,n,u)}):l==un?u?G(en,u[Mn],tn):en:l==on?u?G(en,u[ge],tn):en:l==zn||l==fn?function(n,t,r,i,f){for(((r=l==zn?U():u)||tn)&&!(i=en)&&(t=a[nn[Fn]](function(t){return t[Zn]?K(e,t)&&null:!t[Kn]||t[Kn][nn[Hn]](function(t){!(n=E(t[Vn][en],Ln))&&!tn||A(G(tn,e)[en],n)||(G(tn,e)[en][n]=undefined)})&&!0}));i<R(t);i++){if(G(tn,r[ge])){G(en,r[ge],en);break}if(((f=K(e,t[i],r))||tn)&&G(tn,r[Mn]))break;if(r[Rn])return f}}():l==Nn||l==Pn?function(n,t,r){function i(n,e,t,r,u){e[t][nn[Hn]](function(e,f){A(e,t)?i(n,e,t,r[f],u):A(e,Ln)&&(u?G(tn,n)[en][E(e,Ln)]=r[f]:B(n,E(e,Ln),r[f]))})}function f(n,e,t,r,u){e[t][nn[Hn]](function(e){((u=e[Vn][en])||tn)&&A(u,Ln)?G(tn,n)[en][E(u,Ln)]=r:A(u,Jn)&&i(n,u,Jn,r,tn)})}for(t in!D(u)&&(n=K(e,a[tn]))){if(l==Pn&&(t=n[t])&&en||A(a[en],Ln)?B(e,E(a[en],Ln),t):A(a[en],Jn)?i(e,a[en],Jn,t):A(a[en],Kn)&&f(e,a[en],Kn,t),((r=K(e,a[rn],u))||tn)&&G(tn,u[Mn]))break;if(G(tn,u[ge]))G(en,u[ge],en);else if(u[Rn])return r}D(u,tn)}():l==Tn?function(){for(D(u)||K(e,a[en]);K(e,a[tn])&&(!(C=K(e,a[un],u))&&!tn||!G(tn,u[Mn]));K(e,a[rn]))if(G(tn,u[ge]))G(en,u[ge],en);else if(u[Rn])return C;D(u,tn)}():l==sn||l==pn?function(n){for((l==pn?n=!0:tn)&&D(u);(!n||K(e,a[en],u,en,en,tn))&&(!(C=K(e,a[tn],u))&&!tn||!G(tn,u[Mn]));)if((n=!0)&&G(tn,u[ge]))G(en,u[ge],en);else if(u[Rn])return C;D(u,tn)}():l==Mn?function(n,t,r){try{t=K(e,a[en],u)}catch(i){t=K(e,a[tn],u,i)}finally{return((n=u[Rn])||tn)&&!(u[Rn]=en)&&((r=K(e,a[rn],u))||tn)&&u[Rn]?r:(u[Rn]=n)&&t}}():l==On?function(n,t,r,i,f,o,c,d){for((t=a[nn[qn]](tn))&&!(r=!1)&&!(i=!1)&&!(f=en)&&((n=K(e,a[en]))||tn)&&D(u);f<R(t)&&!G(tn,u[ge]);f++)if((((c=K(e,t[f],n))||tn)&&n===c[en]?r=!0:tn)&&r){for(o=en;o<R(c[tn]);o++){if(((d=K(e,c[tn][o],u))||tn)&&G(tn,u[Mn])){i=!0;break}if(u[Rn])return d}if(i)break}D(u,tn)}():l==Qn?[A(a[en],Ln)&&E(a[en],Ln)==nn[Yn]?u:K(e,a[en]),a[nn[qn]](tn)]:l==Ln?$(e,E(t,l)):l==Rn?(p={})&&((p[E(a[en],Ln)]=o)||tn)&&e[nn[cn]]([p,null])&&((C=K(e,a[tn],u))||tn)&&(e[nn[dn]]()||tn)&&(u[Rn]?C:undefined):l==En?a[nn[Hn]](function(n){return K(e,n)[nn[ln]]()})[nn[Nn]](nn[Jn]):l==qn?K(e,a[en]):l==ln?((b=E(a[en],an))||tn)&&(g=a[tn])&&(h=function(n,e,t,r,u,i,f,o){return(((A(t,bn)?(i=!0)&&(o=t[bn])&&(f=K(n,o[en]))&&(o=H(n,o[tn],K(n,o[rn])==xe)):t=E(t,Ln))||u)&&(r=K(n,r))||tn)&&(e==fe?i?f[o]=r:B(n,t,r):e==Wn?i?f[o]+=r:B(n,t,$(n,t)+r):e==en?i?f[o]-=r:B(n,t,$(n,t)-r):e==dn?i?f[o]*=r:B(n,t,$(n,t)*r):e==gn?i?f[o]/=r:B(n,t,$(n,t)/r):e==Dn?i?f[o]%=r:B(n,t,$(n,t)%r):e==ye?i?f[o]<<=r:B(n,t,$(n,t)<<r):e==Hn?i?f[o]>>=r:B(n,t,$(n,t)>>r):e==En?i?f[o]>>>=r:B(n,t,$(n,t)>>>r):e==an?i?f[o]&=r:B(n,t,$(n,t)&r):e==Xn?i?f[o]|=r:B(n,t,$(n,t)|r):e==tn?i?f[o]^=r:B(n,t,$(n,t)^r):e==yn?i?f[o]=s(f[o],r):B(n,t,s($(n,t),r)):undefined)})&&(A(g,Jn)?(m=K(e,a[rn]))[Jn][nn[Hn]](function(n,t){return h(e,b,n,m[t])}):h(e,b,g,a[rn],tn)):l==jn?K(e,a[en]):l==Wn?function(n,t,r,u,i){for((n=[])&&!(t=en)&&(u=en);t<R(a);t++)if(!A(a[t],tn))if(A(a[t],jn)){for(!(r=en)&&(i=K(e,a[t]));r<R(i);r++)n[t+u+r]=i[r];u+=r-tn}else n[t+u]=K(e,a[t]);return n}():l==Fn?((b=E(a[en],an))||tn)&&((v=K(e,a[tn]))||tn)&&((O=K(e,a[rn]))||tn)&&(b==Ln?v+O:b==ce?v-O:b==cn?v/O:b==ln?v*O:b==fn?s(v,O):b==kn?v%O:b==bn?v<O:b==we?v<=O:b==ie?v>O:b==Qn?v>=O:b==_n?v in O:b==ue?v&O:b==pn?v!=O:b==On?v!==O:b==Fn?v|O:b==vn?v^O:b==Sn?v==O:b==Jn?v===O:b==rn?v<<O:b==ke?v>>O:b==Tn?v>>>O:b==te?v instanceof O:undefined):l==kn?(u&&(u[Rn]=tn),G(tn,a[nn[Hn]](function(n){return K(e,n)}))):l==mn?((C={})&&a[nn[Hn]](function(n){(w=K(e,n))&&((I=w[en])||tn)&&((q=w[tn])||tn)&&(w[rn]?(k={})&&(k[nn[Wn]]=!0)&&(k[nn[Sn]]=!0)&&w[rn]==tn?((k[nn[Qn]]=q)||tn)&&i[nn[En]][nn[Rn]](C,I,k):w[rn]==rn&&((k[nn[ne]]=q)||tn)&&i[nn[En]][nn[Rn]](C,I,k):C[I]=q)}),C):l==Bn?[H(e,a[en],K(e,G(tn,a))==xe),K(e,a[tn])]:l==Cn?(((x=K(e,G(tn,a)))==An?O=tn:x==jn&&(O=rn))||tn)&&(a=a[nn[qn]](en,-tn))&&((_=K(e,G(tn,a))==xe)||tn)&&(a=a[nn[qn]](en,-tn))&&((I=H(e,G(tn,a),_))||tn)&&((q=a[R(a)-rn])||tn)&&((j=a[nn[qn]](en,R(a)-rn))||tn)&&((F=J(M(e,I,q,j),I)[nn[Zn]])||tn)&&[I,F,O]:l==cn?G(tn,a[nn[Hn]](function(n){return K(e,n)})):l==Xn?((C=K(e,a[en])?K(e,a[tn],u):K(e,a[rn],u))||tn)&&u[Rn]?C:undefined:l==vn?function(n,e,t,r,u,i){return e==le?A(r,bn)?((i=r[bn])||tn)&&((u=K(n,i[en]))||tn)&&((i=H(n,i[tn],K(n,i[rn])==xe))||tn)&&(t==xe?++u[i]:u[i]++):((i=K(n,r))||tn)&&(A(r,Ln)&&B(n,E(r,Ln),i+tn)||tn)&&(t==xe?i+tn:i):e==Zn?A(r,bn)?((i=r[bn])||tn)&&((u=K(n,i[en]))||tn)&&((i=H(n,i[tn],K(n,i[rn])==xe))||tn)&&(t==xe?--u[i]:u[i]--):((i=K(n,r))||tn)&&(A(r,Ln)&&B(n,E(r,Ln),i-tn)||tn)&&(t==xe?i-tn:i):void 0}(e,K(e,a[en]),K(e,a[tn]),a[rn]):l==Zn?R(a)<=rn&&A(a[en],yn)?G(tn,e)[en][E(G(tn,a),Ln)]=r[K(e,a[en])]:(I=E(G(tn,a),Ln))&&(G(tn,e)[en][I]=J(M(e,I,a[R(a)-rn],a[nn[qn]](en,R(a)-rn)),I)[nn[Zn]]):l==Sn?K(e,a[en])?K(e,a[tn]):K(e,a[rn]):l==wn?function(n,e,t,r,u,i){return e==Ln?+K(n,t):e==ce?-K(n,t):e==Kn?!K(n,t):e==mn?~K(n,t):e==Bn?A(t,Ln)?typeof $(n,E(t,Ln),tn):typeof K(n,t):e!=se?e==ve?A(t,Ln)?A(G(tn,n)[en],E(t,Ln))?delete G(tn,n)[en][E(t,Ln)]:(i=E(t,Ln))!=nn[gn]&&i!=nn[wn]&&!nn[le]:A(t,bn)?(u=t[bn],delete K(n,u[en])[u=H(n,u[tn],K(n,u[rn])==xe)]):(K(n,t),!0):void 0:void K(n,t)}(e,K(e,a[en]),a[tn]):l==Gn?function(n,e,t,r){return e==wn?t||K(n,r):e==$n?t&&K(n,r):void 0}(e,K(e,a[en]),K(e,a[tn]),a[rn]):l==rn?R(a)<=rn&&A(a[en],yn)?r[K(e,a[en])]:J(M(e,E(G(tn,a),Ln),a[R(a)-rn],a[nn[qn]](en,R(a)-rn)))[nn[Zn]]:l==Hn?J(M(e,nn[Yn],G(tn,a),a[nn[qn]](en,R(a)-tn)))[nn[Zn]]:l==xn?G(tn,e)[un]:l==bn?((q=H(e,a[tn],K(e,a[rn])==xe))||tn)&&((F=K(e,a[en],typeof u!=nn[an]?tn:u+tn,z=o||[],c))||tn)&&(!u||d?z[nn[Hn]](function(n){return F=F[en],n})[nn[Hn]](function(n){F=F[n]})&&c&&c[Gn]?function(){return f[nn[Tn]][nn[Mn]][nn[hn]](F[q],F,arguments)}:F[q]:z[nn[cn]](q)&&[F,F[q]]):l==_n?(P=typeof u==nn[te]?u:{})&&(P[Gn]=tn)&&(S=K(e,G(tn,a),en,en,P))&&(N=a[nn[qn]](en,-tn)[nn[Hn]](function(n){return A(n,jn)?L=K(e,n):K(e,n)}))&&(N=L?N[nn[qn]](en,R(N)-tn)[nn[vn]](L):N)&&!(n>y)&&f[nn[Tn]][nn[Mn]][nn[hn]](S,undefined,N):l==$n?new(f[nn[Tn]][nn[In]][nn[Mn]](K(e,G(tn,a)),[en][nn[vn]](a[nn[qn]](en,R(a)-tn)[nn[Hn]](function(n){return K(e,n)})))):void 0}(Rn=27)&&(on=5)&&(pn=10)&&(En=30)&&(vn=17)&&(Fn=31)&&(ln=8)&&(bn=16)&&(Dn=36)&&(xn=20)&&(ue=56)&&(Gn=39)&&(an=9)&&(kn=19)&&(Bn=35)&&(Un=38)&&(mn=12)&&(Hn=40)&&(Xn=49)&&(rn=2)&&(le=62)&&(Tn=46)&&(Cn=24)&&(Vn=47)&&(tn=1)&&!(en=0)&&(An=29)&&(zn=28)&&(un=3)&&(qn=26)&&(_n=22)&&(sn=11)&&(In=25)&&($n=34)&&(Pn=32)&&(yn=14)&&(cn=6)&&(Mn=37)&&(Jn=41)&&(Ln=43)&&(Sn=33)&&(Re=123)&&(re=55)&&(fn=4)&&(ke=73)&&(me=66)&&(ae=63)&&(ne=52)&&(fe=58)&&(On=21)&&(Zn=51)&&(hn=15)&&(dn=7)&&(je=78)&&(be=70)&&(ee=53)&&(ye=68)&&(pe=64)&&(Nn=44)&&(_e=77)&&(he=69)&&(gn=13)&&(de=61)&&(se=65)&&(Yn=50)&&(ze=127)&&(Oe=76)&&(ve=71)&&(wn=18)&&(Ie=91)&&(Qn=45)&&(ge=67)&&(oe=59)&&(Ce=79)&&(te=54)&&(xe=74)&&(jn=23)&&(Kn=42)&&(ie=57)&&(Wn=48)&&(qe=97)&&(we=72)&&(ce=60)&&(nn="ReferenceError(g(c(call([(lastIndexOf(push(pop(toString(number(valueOf(indexOf(window(module(arguments(cilame_call(charCodeAt(concat(exports(pow(match([0-9a-f]{2}(Date(Math(hasOwnProperty(bind(slice(defineProperty(BigInt(parseFloat(Object(filter(v(configurable(String(keys(length(apply(%$&(vmpzl_arguments(map((]( is not defined(join(get(prototype(undefined(enumerable(replace(null(_(set(decodeURIComponent(object(charAt(0(parseInt(RegExp(Function(fromCharCode(*(require($".split("("))&&(i=typeof global==nn[Vn]?window:global)&&(L=new i[nn[_n]])&&(R=$e[nn[In]](tn,L,he))&&(E=$e[nn[In]](tn,L,In))&&(S=$e[nn[In]](tn,L,Un))&&(A=$e[nn[In]](tn,L,Ce))&&(D=$e[nn[In]](tn,L,oe))&&(M=$e[nn[In]](tn,L,Yn))&&(U=$e[nn[In]](tn,L,ae))&&(G=$e[nn[In]](tn,L,sn))&&(H=$e[nn[In]](tn,L,ee))&&(J=$e[nn[In]](tn,L,on))&&(N=$e[nn[In]](tn,L,ne))&&(Q=$e[nn[In]](tn,L,Vn))&&(T=$e[nn[In]](tn,L,pe))&&(X=$e[nn[In]](tn,L,de))&&(Y=$e[nn[In]](tn,L,be))&&(f=i[nn[oe]])&&(o=i[nn[$n]][nn[ce]])&&(c=i[nn[ee]])&&(d=i[nn[en]])&&(l=i[nn[En]][nn[Bn]])&&(a=i[nn[An]])&&(p=i[nn[ie]])&&(s=i[nn[jn]][nn[kn]])&&(m=i[nn[fe]])&&(f[nn[Tn]][nn[hn]]=f[nn[Tn]][nn[un]])&&(q=i[nn[En]][nn[Tn]][nn[Cn]])&&(y=tn)&&(I=tn)&&(h=[])&&(b=[])&&((g=i[nn[zn]])||tn)&&(z=Be[nn[In]](tn,L,je))&&(F=Be[nn[In]](tn,L,xn))&&(P=Be[nn[In]](tn,L,hn))&&($=Be[nn[In]](tn,L,Pn))&&(B=Be[nn[In]](tn,L,qn))&&(V=Be[nn[In]](tn,L,me))&&(W=Be[nn[In]](tn,L,Nn))&&(K=K[nn[In]](tn,L))&&(v=z(Re,ze)+z(Bn,Gn)+z(Hn,Ie)+z(qe,Re))&&(w=z(Hn,Ie))&&(k=z(Re,ze)+z(Bn,Gn)+z(qe,Re))&&(x=nn[fn]+k+nn[Kn]+nn[de]+nn[fn]+w+nn[Kn])&&(O=m(nn[On],nn[tn]))&&(_=[[i,null,null,e,t,en,en,arguments,{},L]])&&(j=_[en][ln])&&K(_,function De(n,e,t){return function(n,e,t,r,u,i,f,o,c,d){if(t==an||t==Ln||t==dn||t==Yn||t==yn||t==Dn||t==en||t==gn)return(r={})&&((r[nn[rn]]=t)||tn)&&(u=function(n,e,t){return(t=P(e))&&[Y(h[t[en]],t[en],n),t[en],t[tn]]}(t,e[nn[qn]](y,pn)))&&((r[t]=u[en])||tn)&&[function(n,e,t,r){return((r=b[nn[sn]](n[e]))||tn)&&((r==-tn?b[nn[cn]](n[e])&&(n[e]=R(b)-tn):n[e]=r)||tn)&&((n[nn[Pn]]=t)||tn)&&n}(r,t,u[tn]),u[rn]];for((f=[])&&(r={})&&(i=S(e,y)[en]);R(i);)(o=v[nn[sn]](i[nn[qn]](en,y)))!=an&&o!=Ln&&o!=dn&&o!=Yn&&o!=yn&&o!=Dn&&o!=en&&o!=gn?(d=S(i,y,tn))&&f[nn[cn]](De(n,i))&&(i=i[nn[qn]](d[tn])):(c=De(n,i))&&f[nn[cn]](c[en])&&(i=i[nn[qn]](y+c[tn]));return(r[t]=f)&&((r[nn[rn]]=t)||tn)&&r}(n,e,v[nn[sn]](e[nn[qn]](en,y)))}(L,W(u)))}("jsvmpzl:ver.1.5.1", this, typeof arguments!="undefined"?arguments:void 0, [], "hWm=#hh|q9#j{gs;v$bdr/tomd#>#ie%m,qidhjWt%#|q2tm$|%>seimx.qi$#bFa$iyc8nnpt%?fpt{tR|jnskkM|o%~fnX|h%mkiR|grhzd+vhhef.|%n&tn2|gxjxi+biteb8v#tw}1|d&~$zB|rcz&.|%yqpcW|grsayI|p}zjy-bm}ogCagqw%JshpqfYwnroiZ%jo|y,v#vmiM$|gmy6t%mri*w$bfk?%{jljSvcqvo*kr%zsXj}f$hVf{bqo.|bkpa+afcaz2i}&xm8jmdwq(i|#ldT|gbpguHqtxe}B|chybxNz#xq~?#hf|jPmzk}jJr%aaj>i{u#bHjsw{jB${pf{:ewk&xK#j~y|BitetiDljqx{J|%hf$wPv{cdlJ|eq&f;qsvleW|o&mk}Cyo%nq+|%v{nuS|ob}rhHkt}wz+kt{p~<ao#p{S|%w}wvL|ol}x$3|crf%xY|%klwq-|ged#hS$e&wuNnqyx~0oypew<oxiqgKn{rjy+n$xss6|cmfcP||yqd{Rlsfq$+may$yCmpzhr<n{&j{Uaeu{jL|p~jeu-b$ych,|sfxee5|kc#{oQoik&{1mjdsj.|nnniZbjhceP#hcw$-ilru&+nixjjNaal{k3|}ptkcVay~jg)|cm{cz:a{|ur:ad|dj0&xz#k*r|bvd5gqh$Am%yc~T|fymohYqhcfd0|rkjfbF#|#&yX|butei)flvto@h}au&4flo~r;a$dtc>q%g|eXu#czfZz%g&~?rpr#=#dld{P|otjplCufaf{4#kvv%Mz~c|uTu|cqfSm%ftuL.<m7S~;KH#~4J9O7K463R|40.KHK=)(J9O7K563&+0/K1K|5)(Q}:?6)|20/K4K|6)(.-#|XTA(?))K469R|0040.K4.-)*K=)(T|:6|7H|+K6#ZT;(9))K663R|70.K6K=)(TC(A))05K50/K6.|1)*)*0.K6.-)*0/K4K|8)(K+3*K5KIT6(4))0.K/KJ)(P(J:O8KK040.KLK2)(KM)(Ta7(a4))040.KLK2)(KM)(}&TK3#&MQ&8GO)C0.K3K0)(?C)>69R|9040.K3K0)(K?)(2,)@.-#%=J@O>K96:0.K3K0)(00-|:K|3)(Q$SK9#$LJ:O8KN04K/0.K9.-)*)*J8O6K5620.K3K0)(KIT#V(#S))04K/0.K9.-)*)*}#@KF##9J;O9K,65KFK50/K1K|;)(J.O,K.,(T<(:))0.K.KD)(0.K,KD)(T<(:))0.K.KO)(0.K,KO)(T<(:))0.K.KP)(0.K,KP)(T<(:))0.K.KQ)(0.K,KQ)(T<(:))0.K.KR)(0.K,KR)(T<(:))0.K.KS)(0.K,KS)(T<(:))0.K.KT)(0.K,KT)(T:68K,040.K/KJ)(KG)(38664*K;KA0.KNKB)(K+K+K+38664*K;KA0.KKKB)(K+JDOBK<0>680.KUK2)(0.K1KV)(KW)(T?(=))0.K<K:)(}1#-3+D|-K+T>6<0.KUK2)(RWK<0.K1KX)(T6(4))0.K/KY)(P(T7(5))0.K/KZ)(D|.T$D2$A)|<6$;}$8#$3JEOCK70?690/K|(K2)(0.K1KV)(K0)(J5O3K|)0.K7K:)(J}HO}EK|*}}?#}:J=O;K8674*K;KA0/K|)KB)(Q|OG|2)C0.K/KZ)(GY)|/?=)>63R|=0.K8K?)(2,)@.-?=)>63R|>0.K8K?)(2,)@.-#>T<6:4*K;040.K/KY)(KG)(K+3*K8K:T|E6|B0/K|(K2)(R0,|,C/K:K|*)(C4KE0.K7KE)()(C6K|+0/K7R|+)*)(C6K|,0/K7R|,)*)(0.K1KX)(K+")
        """
    })
    webdriver.execute_cdp_cmd("Network.enable", {})
    toggle = { "chrome_close": False }
    webdriver._quit = webdriver.quit
    def quit(*a, **kw):
        toggle['chrome_close'] = True
        return webdriver._quit(*a, **kw)
    webdriver.quit = quit
    webdriver._close = webdriver.close
    def close(*a, **kw):
        toggle['chrome_close'] = True
        return webdriver._close(*a, **kw)
    webdriver.close = close
    import time, threading
    def hook_close_window():
        toggle['chrome_close'] = False
        while not toggle['chrome_close']:
            time.sleep(.3)
            try:    driver_logs = webdriver.get_log('driver')
            except Exception as e: 
                if 'Failed to establish a new connection' in str(e):
                    toggle['chrome_close'] = True
                driver_logs = []
            for i in driver_logs:
                if 'Unable to evaluate script: disconnected: not connected to DevTools' in i.get('message'):
                    toggle['chrome_close'] = True
                    webdriver.quit()
    threading.Thread(target=hook_close_window).start()
    return webdriver

def wait_exit(driver,xpath,sec=10):
    locator = (By.XPATH, xpath)
    wbw(driver,sec).until(EC.visibility_of_element_located(locator)) # 判断某个元素是否被添加到了dom里并且可见，即宽和高都大于0

def get_verify_src(driver):
    driver.get('https://gt4.geetest.com/')
    wait_exit(driver, '//div[@class="geetest_btn_click"]')
    driver.find_element(by=By.XPATH, value='//div[@class="geetest_btn_click"]').click()
    time.sleep(3) # （滑块出现时，会有短暂的自动滑动动画，等待自动滑动结束）
    wait_exit(driver, '//div[@class="geetest_bg"]')
    def get_image():
        return driver.execute_script('''return (function(){
            window.toggle = false
            window.getBase64 = function getBase64(img) {
                var canvas = document.createElement("canvas")
                img.setAttribute("crossOrigin",'Anonymous')
                canvas.width = img.width
                canvas.height = img.height
                canvas.getContext("2d").drawImage(img, 0, 0, img.width, img.height)
                return canvas.toDataURL('image/jpeg')
            };
            var ret = {}
            for (var i = 0; i < window.image_cache.length; i++) {
                if (window.image_cache[i].src.indexOf("/slice/") != -1){
                    ret.front = getBase64(window.image_cache[i])
                }
                if (window.image_cache[i].src.indexOf("/bg/") != -1){
                    ret.bg = getBase64(window.image_cache[i])
                }
            }
            return ret
        })()''')
    imgs = get_image() # 由于一些缓存和异步的问题，这个函数需要执行两次
    imgs = get_image()
    front_np = read_from_b64string(imgs['front'])
    bg_np = read_from_b64string(imgs['bg'])
    return front_np, bg_np

def drag_and_drop(driver, xpath, vlen):
    move_ele = driver.find_element(by=By.XPATH, value=xpath)
    from selenium.webdriver import ActionChains
    action_chains = ActionChains(driver)
    action_chains.drag_and_drop_by_offset(move_ele, vlen, 0).click_and_hold(move_ele).perform()

def drag_and_drop_tracks(driver, xpath, tracks):
    move_ele = driver.find_element(by=By.XPATH, value=xpath)
    from selenium.webdriver import ActionChains
    ActionChains(driver).click_and_hold(move_ele).perform()
    for idx, (x, y) in enumerate(tracks):
        if idx > len(tracks) * 0.9: time.sleep(0.05)
        if idx > len(tracks) * 0.8: time.sleep(0.05)
        ActionChains(driver).move_by_offset(xoffset=x,yoffset=y).perform()
    ActionChains(driver).release(move_ele).perform()

def get_slide_track(distance):
    v = 0
    t = 0.2
    tracks = []
    current = 0
    mid = distance * 5/8
    distance += 10
    while current < distance:
        t = random.randint(1,4)/10
        a = random.randint(1,3) if current < mid else random.randint(2,4)
        v0 = v
        s = v0*t + 0.5*a*(t**2)
        current += s
        tracks.append(round(s))
        v = v0 + a*t
    temp = 10+round(current-distance)
    for i in range(5):
        num = -random.randint(1,3)
        tracks.append(num)
        temp += num
    tracks.append(abs(temp))if temp<0 else tracks.append(-temp)
    for idx,i in enumerate(tracks):
        tracks[idx] = [i, (i % 3)]
    return tracks

def chech_geetest_slide(driver, times=0):
    status = driver.execute_script('''return (function(){
        var ret = {}
        var x = document.getElementsByClassName('geetest_tip')
        if (x.length && x[0].innerHTML.trim()){
            if (x[0].innerHTML.trim() == '验证通过'){
                ret.status = 'success'
                ret.info = x[0].innerHTML
                return ret
            }
        }
        return {status: 'unknown'}
    })()''')
    if status['status'] == 'success':
        return True
    if status['status'] == 'fail':
        return False
    if status['status'] == 'unknown':
        if times > 5:
            return False
        time.sleep(.5)
        return chech_geetest_slide(driver, times+1)

def run_by_thread(func):
    threading.Thread(target=func).start()

def verify_login_slide(times=0):
    driver = get_driver()
    try:
        front_np, bg_np = get_verify_src(driver)
        tlwh = findmatchtemplate_np(front_np, bg_np)
        tracks = get_slide_track(tlwh[1]-10)
        drag_and_drop_tracks(driver, '//div[@class="geetest_btn"]', tracks)
        if chech_geetest_slide(driver):
            data = driver.execute_script('return window.v_cache_src')
            run_by_thread(driver.quit)
            if data and data[-1].get('data', None) and data[-1]['data'].get('result', None) == 'success':
                return data[-1]['data']['seccode']
            raise Exception('unknown error')
        else:
            time.sleep(0.5)
            print('verify error retring...')
            run_by_thread(driver.quit)
            return verify_login_slide(times+1)
    except Exception as e:
        print(e)
        time.sleep(0.5)
        print('unknown error retring...')
        run_by_thread(driver.quit)
        return verify_login_slide(times+1)

for i in range(3):
    info = verify_login_slide()
    print(info)


# driver = get_driver()
# front_np, bg_np = get_verify_src(driver)
# tlwh = findmatchtemplate_np(front_np, bg_np)
# tracks = get_slide_track(tlwh[1]-10)
# drag_and_drop_tracks(driver, '//div[@class="geetest_btn"]', tracks)
# print('验证状态(true为成功)', chech_geetest_slide(driver))
# # driver.quit()