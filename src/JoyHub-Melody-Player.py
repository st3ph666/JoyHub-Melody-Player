#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
import socket
import re
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

VIDEO_DIR = Path(os.environ.get("JOYHUB_VIDEO_DIR", str(Path.home() / "Videos")))
SCRIPT_DIR = VIDEO_DIR / "MelodyScript"
PLAYER = Path.home() / ".cache/melody-player/melody-ble-direct-engine.py"
APP_VERSION = "v2.5.3"
APP_NAME = f"JoyHub Melody Player {APP_VERSION}"
PYTHON = Path(sys.executable)
CONFIG = Path.home() / ".config/melody-player-ble-direct-gui.json"

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v"}

VIBRATION_PATTERN_NAMES = (
    "progressif3",
    "regulier3",
    "double",
    "coeur",
    "rafale5",
    "pulse4",
    "pulse6",
    "pulse8",
    "court_long",
    "long_court",
    "triple_sec",
    "triple_large",
    "vague4",
    "vague6",
    "escalier4",
    "escalier6",
    "syncopé",
    "staccato",
    "lent2",
    "lent3",
    "rafale3",
    "rafale7",
    "respire4",
    "alterné",
    "surprise",
)

VIDEO_TYPES = (
    ("Vidéos", "*.mp4 *.mkv *.avi *.mov *.webm *.m4v"),
    ("Tous les fichiers", "*"),
)


LANGUAGE = "fr"

TRANSLATIONS = {
    "Vidéos": "Videos",
    "Tous les fichiers": "All files",
    "Aucun script sélectionné": "No script selected",
    "Choisis une vidéo pour commencer.": "Choose a video to begin.",
    "Aucun": "None",
    "VIBRATION FUNSCRIPT — clique ou glisse pour déplacer la vidéo": "VIBRATION FUNSCRIPT — click or drag to seek the video",
    "Pause / Reprendre": "Pause / Resume",
    "JoyHub Melody BLE direct — connexion mémorisée + schémas vibration + R4": "JoyHub Melody direct BLE — remembered connection + vibration patterns + R4",
    "Sélection": "Selection",
    "Vidéo": "Video",
    "Parcourir": "Browse",
    "Script": "Script",
    "Réglages": "Settings",
    "Vibration maximale": "Maximum vibration",
    "Maintien à zéro": "Zero hold",
    "Lissage": "Smoothing",
    "Vibration minimale": "Minimum vibration",
    "Amplification du funscript": "Funscript amplification",
    "Amplification vibration": "Vibration amplification",
    "Activer le contrôle PUMP / R4 (CONSTRICT)": "Enable PUMP / R4 control (CONSTRICT)",
    "Contrôle PUMP / R4": "PUMP / R4 control",
    "Ouvrir MPV en plein écran sur l’écran de droite": "Open MPV fullscreen on the right display",
    "Activer le PUMP / aspiration Melody": "Enable Melody PUMP / suction",
    "Durée du PUMP": "PUMP duration",
    "Durée du relâchement": "Release duration",
    "R4 répété toutes les": "Repeat R4 every",
    "Pause minimale entre PUMP": "Minimum pause between PUMPs",
    "Pause maximale entre PUMP": "Maximum pause between PUMPs",
    "Schéma vibration 1": "Vibration pattern 1",
    "Schéma vibration 2": "Vibration pattern 2",
    "Schéma vibration 3": "Vibration pattern 3",
    "Choisir aléatoirement parmi les 1 à 3 schémas sélectionnés": "Randomly choose among the 1 to 3 selected patterns",
    "Supprimer la vidéo et ses funscripts à la fin ou en passant à la suivante": "Delete the video and its funscripts when finished or skipping to the next",
    "Passer automatiquement à la vidéo suivante": "Automatically play the next video",
    "▶  Lancer la vidéo": "▶  Play video",
    "⏭  Lire le dossier": "⏭  Play folder",
    "⏩  Vidéo suivante": "⏩  Next video",
    "🧪  Test aspiration Melody 10 s": "🧪  Test Melody suction 10 s",
    "■  Arrêter": "■  Stop",
    "Choisis une vidéo avec son funscript": "Choose a video with its funscript",
    "Aucune vidéo en lecture.": "No video is currently playing.",
    "Durée de la vidéo inconnue.": "Unknown video duration.",
    "Choisir une vidéo": "Choose a video",
    "Funscript original trouvé. Conversion vibration automatique prête.": "Original funscript found. Automatic vibration conversion is ready.",
    "Aucun MelodyScript correspondant.": "No matching MelodyScript.",
    "MelodyScript introuvable": "MelodyScript not found",
    "Python introuvable": "Python not found",
    "Erreur du moteur intégré": "Embedded engine error",
    "Erreur de lancement": "Launch error",
    "Fichier introuvable": "File not found",
    "La vidéo ou le MelodyScript n'existe plus.": "The video or MelodyScript no longer exists.",
    "Erreur de conversion": "Conversion error",
    "Aucune vidéo actuelle à passer.": "There is no current video to skip.",
    "La vidéo actuelle n’est plus dans son dossier.": "The current video is no longer in its folder.",
    "Aucune vidéo suivante disponible.": "No next video is available.",
    "Passage à la vidéo suivante…": "Moving to the next video…",
    "Vidéo introuvable": "Video not found",
    "Choisis d’abord une vidéo valide.": "Choose a valid video first.",
    "Erreur": "Error",
    "La vidéo sélectionnée n’est plus dans le dossier.": "The selected video is no longer in the folder.",
    "Aucune vidéo lisible": "No playable video",
    "Aucune vidéo à partir de la sélection ne possède un funscript correspondant.": "No video from the selection onward has a matching funscript.",
    "Toutes les vidéos du dossier ont été traitées.": "All videos in the folder have been processed.",
    "La lecture du dossier est terminée.": "Folder playback is complete.",
    "Terminé": "Done",
    "Lecture terminée naturellement.": "Playback finished naturally.",
    "Lecture fermée avant la fin : aucun fichier supprimé.": "Playback was closed before completion: no files were deleted.",
    "Arrêt demandé… aucun fichier ne sera supprimé.": "Stop requested… no files will be deleted.",
    "Contrôle MPV indisponible : socket IPC absent.": "MPV control unavailable: IPC socket missing.",
    "Suppression partielle": "Partial deletion",
    "Aucune vidéo suivante.": "No next video.",
}

def tr(text: str) -> str:
    if LANGUAGE == "en":
        return TRANSLATIONS.get(text, text)
    return text

def normalize_pattern(value: str) -> str:
    """Return the engine sentinel regardless of the UI language."""
    return "Aucun" if value in ("Aucun", "None") else value


COLORS = {
    "bg": "#111318",
    "panel": "#191c22",
    "panel_alt": "#20242c",
    "border": "#2c313b",
    "text": "#f2f4f8",
    "muted": "#9aa3b2",
    "accent": "#7c5cff",
    "accent_hover": "#9278ff",
    "success": "#39d98a",
    "warning": "#ffb84d",
    "danger": "#ff5c72",
    "track": "#343a46",
}



ENGINE_BUNDLE = 'c-q~4+jbjClGr=GBBylv5a<R<;6)M}7TU`uscG&|BoC?9tXHE`rwAm->Mm5F>%t~SL!WuH-~HmZJ$|r9vtQt|Z^J*CFL6ZVr82XsKtL_;jNSH*h^oxU$jHdZxMkFnUp+1J?CE8cJmtv^Tig}bX|mn%Jg;-iCj~Dvb`wn>KBnv|HY<~Sl0}OG9$jW(5v2)Rq|o9xO3GWm(;2YiFqv@n`s}R_KQ1_%q)CEc*u%fDqojytA-vw_Ns)yyTZ9?=Ex)`-CqME6JM3SF*%fDH!u)Ei>0kf&-=n19Ngfps9~n<3Dd5Ax2p+IehtYpS@edobFv}kPT*$|pgU#WP9vcv*yuu#_Jxp%Wh||+7jCc+>&*xz>g}=Tni((O%SM0Pb7G?3~Zo&PxN8g_By*Wg5_h=~2V$K#19|75G{NJBSc#>v0{tJX)JTCxgm~5GImX>VBv-!hEpw_{|#|2NONU>Z_M3SEk=4=ry0O`C4<CqNw<>D#}0mVy+5w*_CY05$%k!m+z+;lpJw|u?;lmtZosp>Mw(jv_628%en<C(v>V;-z5PyP8~$6KeZ`WxC*%j6NubY@vPXF)J4i!$Ruz@qsg%?cJK2>?Wb=besvmR$h@<Xr#G?~+NBs-Krp4veFI{gA_2$-mQF{guHorE~QwkFJt1*1w3W^sn-Ak)=Rr-8a9}e-=QnSrltbifGQoOcr5r9Y>dH8fWlRyeRG#QF5i8?<IGgPLbUSl2e1rn1?^A_ut}={Wt=??~5N76CerCI{bFRVF8b*-C>rcnPh|v7`7|9m@)5lIxS&M|MIUA@L&Fog_k+N^M99kRkI_(2z&r-!y7(fBle%GMHQ<#xPgsM8{T9w0_*iPD5S?2XyoU`lxLZE(WC!`T>_kZahC(#4sWBPyVa}BUTqvnfNCacOG#?z=Lh^InsBkt_QeLQURK*r;jt#&&S+l|`4na=Q_y;CZBZm-3w@nVD=tEPp97pvUz5(k;j6vxkKY6rhv#n(&p`@$Kj)*TPdB$-_(S-Ao1@LG?VV>{)oy?91RC$3o*Z02>s^1SU!9#E9|y1T>2~$-;BfEY+r5(mcna_~_49u|JU<P-J3T%SJzfl}E*EEqhX=vM>(kRW-yNO&ntJZ;>esK2PJ;9APfp+!4Eb9^8W7zwhJ1Upe~450$Mo*I@{+ygaXP&N(ev%`VQ{kdTD%*m$N2QstG!KpI)wjbvv6~Of8fb59PHx%42QeJXS1&_w|8cjqQ~CB!TI6EMX<lO{~ZFvjqhKlbKdQ-r_A#w;pCb>ozoa{MW6mKkiWy}Gy_577q=i4J5SiYK2P8@oJA=8;qM&IO*jj!S@<+KoG`)Z35<GqSMc1&4Ry_LyWZZA4Y%2=R}79c@&EVsyk6A>-n8_Arn;N%bN2n~v*7jKKQ(tcP@}wnuCmAZ;ql?##bIlQP3o{II&{QAd31UbobA1Nb9jD&tnh)j)dN|4g*1w0+un%1>%PfK-lv7`^;!2-80X^W5PzzdTf-$Ux1E=}z4u~&cp1McLD*!@NV|6XEfd&UFRPKJX$fM~8fI&22_)wwOhG}Kq@Z{$qs(yE0<_x(C<|v{%%54HhIZ@Wa}(6R&r6uO!f;W-vz-b-nCeciFPqXTzyERvl+Sni(bmxJ{M_n1G&;km@4tL*bvBlZI`5jDhcC>|&!O|K-TAq(LS<G2ahhDUj!r-1i|uE|3uE>OARt&K7^}4j#)5BvDL@5_c>o%dHJz``>AZmHY}<s~bpgbvf14n-EKGLlASxVg!mH9*$Sr#<s%h-Dyx7`ld9mFxaT?TOfZ?vahW%!2%oopFUTh89UhK5JFb6mIl;@KWWzfztR&7DZBu^Vb?QwT%<E}`d&9)b9^WA*0HtDvT7ZR2K6s)LrM4z=lr*(a_$Ma?af!;Nlghgr%``ncRFWN*%4Ep1i*>}g;=l#YPhJZ#0+t%K<q~C6R$31t1`}VT6t@Yk<dcSCwf6r<&H#izj??sf^`+ciT`dRF0uGjW+Tf9`{GO1w5sW2{hme_3K3dLrjVQsK2n;Tm8k-?p129`z6+e!VRg$cLJL!eb24r{Z$2lX9QD5X3F`~PVlR4~+`w)~w=XUb=l7b5^W73mTHI~TmGekI|Yk62!0ea7Q(k@IPgkJv0u!=lFq->{+tng8xGP2)cLN8Sq)3helEUcix*a29Vod<2l}^yDe3m%M-{5va1aY+ACMU(JDg>Cega!^e5Z@FWYtq(WZ+nPUPIK)S9C`d8er)J&W!i>IZRr9bwyYP0DBfA&nXD4MY(EfnyPhMVyM=EtOV(xK-?3N{#EnwRtLJiP6~5)C)|f?VBM7EXFSHcK-mhzu{_5s*y*7XvP?L$JffOhHinHT`>NKs2mtk9~po3sffMyo`lWC2VRKmdFk|6pbFFi9n!-81ST=^UPTJUNutz>Z>tpo6=J;aoqt(CMNMx^sPV{ghQUunDqJrIf1*`LZb6-u=)Po5LSkPw9`1U0ow!~C$|qnb_U%!m;t0f*il_LyAo7s(qyXHR$!x@4HDs+$>v9SfYx%iXQLmIWrhn>?~?Iw8Wj8%77JaBQF1l*%3?Oy^?G1%gMQTQS+HPS3C<p)azo6#Jvp8*?-*Eq^AzL=7=UcVKFIF(Uatl~Qc<>`*V5&2dSSRb#LmfcLHcQ#aZmz*Y)q{8^NImYV)n#%1#DgrA2(o(f>qzqoTi^6Z^3rH;$2`GqxDy8)1a&4av>-nLBK%H;Qx@&C?S+Z&V<XeU>_=MM_2bupa#G_2U52}=Y#(9{%Q4he&74+AOC07ts>@>d`dXG@aHfpEYF)ijq*u)!?P}W`_i%)SNQZgmCFU_A;2IpB*2l&2jaPpvWtPG&$_ksRL%*10$XdA#?x-E0!ST=H?`h?geNwIw_>keJ5Qe3u4-H#V91zH@Fanw6*<!w;hz2VkN-_Sk-m*4mbEseJ9m4lEy4^PZ}T6gQPved^05%c{5HyqApMbk_Ev=Va~6RlqP=V5*=M!ATm#v*uPoZ(9&6d7_J|!*E>*1i(%3)t5Mo)h#|q9X012lqtjEJgpPi)T4Uc1Pz=G|Qvn{=2kooOd32vAEbU%+dUv#(NZ0s1W!t*jg#-}+O{!)zwAeF(;;U)S(7umy~a<*;E!8i7)_ZE3+7IF4dxe>(_@Cf6$oMW`6z=yTS4>pl;5KkW0?nzMGb|>T`9@*~mMTma=k#Iqg8gr5+QUr^Mi*AxBuHdu@Cf8xsRh~cvqR&u=O_Q9DN%g9ukcTrk-)6HWMA#o_Tn7PIbJ3PXIX%X$iyDZ;363Qd5u3W&Nd06J)3J!rXNJ44*IBmWq+&h}OFH#><{5KH|A07fPnpgnhJV@X#m&*#zIchm3W6w!iXiCbJf8Js=mnM1>k+w59V$`m3R?O`LsYz~U-f1q`C9go<cD7PkKO#ToB?m4m(ug>HyH<s2jV4~qH-m+L$%~`W#lB}u^<%>Xuk;rZJ5ZEUzYe9+xznr7CTL%N!K_-e!h-y|2pqM{SjSX>Y?0Y#ifx?!ZGhQ2=`Xui`_MCC9tmiwf8Fc{^aPN)PngJr~AJNF5a9U?!E4{0`qfTT*mMR2-U9KI8AMBmISRm$jT&vPC=Zepi2=hYBzKnL8u}7Xv1_}YBUeqg1G7{NzvHI*oNz#53S_aRGY+U&b!UnwePydbLdf74+f>denQ^A5j^I|d!b@s6b)=C6!lXMw9--gjD@9S4hm(1X5g;Ey{UM)8;a(PJsS3n$=@g~QA*k^S_!NBHBuE!2snL~byHHKw*M(kBlo|`0vNFvHr>0u<nBGq0{&>9M12B+`ul>Qu(o0WJftRwP?l`qQ3%VbXpSeMv3Rc70z+=I8hy&~V2x0n9=lB|7;{id!Yh=O7)AG|<$RIbEbyU5D^E_}8)-uH>y4_>pq+t@-Spo6nRC$i!XnM`ao6jE`R<LpUe%=Mlgh@sN?`+Y<I=-;YG*yslB1y!$CcdZD@xR4GwPc5vc=IAoi1W10ui8r7)OcAZy6^gLXj6vi)r4a{{EC(GwF3)2`~E!r-nhz9{bhUBxs$PfnACyDfx1c9Jx(E^YU_n`43(l)-sLImJ}+KNzx$Wvr?I|=BOJq>PGM0>(r%llQ+Rac^Vd>R}&?;$crpp@T|C#8#GDh<lL(7N@YA(Yp1sMJI@5<5s>$_!K#(kvWv9M&$#bR1-QnJ#O@>z!PqlY8heC!noT&!=kbdBA>)&qZo5$Iv**vAZ9nfUSuW{KlLNQ$QRAFLIa?NoLekx0@)%IUn!c;Tq1#FfR<)s>)ps;K<CmW=;;85n4f|}f=W+%0*P85G<wAX>5}8`H+Q~JaN6B)9R<r?x#2@y{kcg7Y14TGrBUHoD_xc_>y?bwWz`P{Y9NRQBAr%sgin~e7A8ATf&=t>=YD!a7&sq-Y+VT5y1gg3*RUdXz0;0>SS=xg<x&p}qC)+HVTt~b?bDAO}kbg!?&aP}+Et^!1x>En@i?;uGae8t<(v_alI3RX-nKf<0w_#ki2{u>#iKC25HAhVG9>kjf?Fh7<$aNC$jMGUhGt5fPPsla-*f7=Qc8YRJ|4AmiE8FyG9ea<=#5?ASv@GG`KtRhAl?j?hUQoiA!sjplX6-dFe#;oF`K9b=`N0Grlu3${o1{Z+I(;^cCPi=6Bdk&5BLfWmBm(3+FD$(Gb!8gX(P;-y+=hywe#7r1M`2=_{IjBOZ;dlIL@RE%Y6nGmKU|<QwA&4V=;WS<f1;$jIfOp|@m{ajuwEdnv!eSWzZ=Kl{BjyH9`iYQC*&XKX|K9HVP}}3JLToA<^(u2<_~|KbCGw3OFqH#H@g8&0{J}USrR?`DdWC|QYPptTupS@tfJY>rI`dt{!;n3j1#c&SOS0_b)p)LnQCY+aNOjQm)#W6MZaFh-HmFdkL<m@a#F&klk>a@V^G$FV-BQ<PKvFo@|AFq12sr|B&VLgLr&T2y}7{OCyeAjY3dyFuOI#e4xkXdyHNs*nq%h-G__cWxI$(fvylO14!nxW9Gn4Do=<?0C|g<o4bNp0f5{PKvjTAv&v-Bep(^H}{VrBq%ZfB$kVww6=j=k*6_E&d0z5t?#55`22~YzDT(tSVxgSunBr-U?YCWbADicJ_aYOe(6Dl1CLN(`2iV{>HzhOgSQ#Nqlyi{+7H7R2N9Iq~IC_GVH1~3SQwDqh<^@c50w6*4HOEoNmC5l=(LjP@YHJolh**TtWbM%2zs2MnX0ZSg1a9#^`*Nq4l-`vh79|6TTUB5f^3)GfV*bfowrh~14*@1oQPjS-%EiL#fkugFUT;M5S^)=MBiVvkuI*;NwQh|UGN@G&uBGY0N%Q2P-^}hHg$fB!j;p!AZ$AKlIvjzzSnA$NXwd!ZXj;m;!^3K>~)a)NHb{tLSytq!M_35F^3UqdZkt84+&`kS=NidHJE<Lq<L;8f%OW^U^3n3IiBc&*{%ojkqQM+n>o(Bdmwk^QC5=<)CaOnGZuY@OU*Gi~`&Vs=IlITVlYdSH2j(T4l^)xH?lmS$K*z2(`<(#b3NkDj6&8ul4RLX$yNObIooDquZ0Bh+ps!NwS46_FRknVLc!UV>Oz$_=>u7Qg?AZQN+IT&8iZP)W*{>F_E!>QBMcu7MM62wevZJ%9;rtoa$eGsiM*ZtlZ^Orz!p}em`;)(=#PHA#j?f~_)E%QLGg=%KyN(g5pEl-T+au&=NH|DxDgjD)?f2Krk%(1o9%<>`=Udrmei+_eD8u>5faw;E=xtbopFmD=ogF%!m%3=^LCIg`wjz3s#->NaRouQRJ_!)M2`t$gX=l0tlIbRGAi*b_LZ=z|;?T6^;r<of}@uf9YYjG@VK?xpb?p-xwE5`K-7U?7{UZrI+C8e&(gnZ01M!t>8hb!-KVBGfmB0_1(Mvb?$45ztmL>dvu$#n|0R2D2ahU+;+>&56g9NBP}CQ0Y$=@H2n<R6oJS-ft@sSz(yx?&R)U<!?l`!>KN^}BEVj_q@k2c$i8CHc(90MEY3(dn4E302w%rh?d)>hdae#F~YXJR(Bj^-wU-Ju4`+1HEF>f7=u}v9e^E;G_!^jKJMk9~6<e5oLtcmkA^O4Vn&lSJ`taEzRt?2Gf!8;a)j3at3rfz8-hSB$$#HX<A(SwaAT3MfhEE<`7=P&e=#27*#Qlr<az}k86$gX@m=HuoPvIblhCFDzV1MU^8iA$k1tov3hdSj8)3Tb(jZYkghRS&(wUPNhp;}H|X`D!u8&O?g>p>{j3?5&@)Ff&+Oimd!#s;v3DP6y7%v!(rPLc?>*ZXt#Ggp5`*qa@fKiB-fG;4<|ee7G$j#D(oCdB$or}0VNvB)*)+9sr3^glAqs`a<H=0#YZkhLS(Bx{Jd`nO-ar;Zn1d8(PkRku{_?M)lb+8#IoaA==#n;LcLvJdu>BT#wwjEeZKlZv-p562(~#}f^y{<r$hn~e%1V>eh~oq;G4D#4<q2rgWoo5cStlh=Zqhr@njDKkv>f3%CC)gdtXHOj<MLJtySx&P9v(x%m!}^rOEwQ<k;RE}m7~&)q7}4x--06!4>^~tOq8@*cI(w%#iqm8T474=tlJcNs=b~WTW!d-Qp7_SV39>C7o$czVMVM#IXLsMdcgka$;F%Vqy0CJ(2cskCbuNm_WI-sXXxYR?1e<&77VBY*#>q?pT!${XGhgFeatLQggt3sV2tZmfcb33(VN5KG8zbXsEAEThnc;SV(>tL;*Ex!SPaor`))rg4`^cAT;O82e8oeMJ_W2eo@0SfJiEqnw`R5}+3torW!_9%{+gUR>Q3F}EVCxfTW3&{`JLy&@KzdNydlawFe5h8ckf5rvljWYVE4u`2<(`{QKR$VGQQww(BZa$m3@Y)NgUqk+Y*$Dzx}Mv^XEK%_#eogSUQ3*jCHa%-5v+F%p*WA$D8nFoRjnSd`G(m<j9hpHfiH_<wKdKO$t-xAXP6%Yo_)oHx6cRvzL0xk0ujIHh-qrTT+Jj+aPZNHW2XC0;N7+nJ#3kQ&oBJPe7FC3)p$KhYASs2D@7RmDsr#jh+^m5SYRCAtZ??Q!b5MK#L9akyH`Nyk;O#_3OI71>4B|)C!lA!@I8o+m!S!CS<4Q)}mXMeW9}9YSGV@)Ud`_Sv@_vOyVf{vD+91YfWpbr9A&4GOkR@B{Xr#eFnV7(PhTI(1Kx8*@C{eLhh@&0>3<wc2lQL8-uHzPyBkm1N$jKCy2=Bu%WFWdB)GR$QhHQ>8zH^Z6JiZ2zFrxr;&|>aty95dLRBP%x{91H*j+kPcIj@&WIvWt(J~gt%j3dZON%BjanrJQn+Gi9(8;8*kmZW_~Gue)zUC!5_Bc?Fj-)ASx0^?SxrLk7vb#k`RxMcSLT?X;e&OM#y7lcy9<P`vcbQo7VNDk)MTda!-7$_)z(Xmrf{3tNinpEDJLS3wV9l`==QDisoOa&z!nE}MGCuvn`dvnY^Rm9i>e}1u(0VQ0wte@#|^YHy)2HaAdVYyi@FwimNHZYmzQnHLwatEvgU^DG_VW(SMf>DYNJu7CKmd3Q>?VZnF3~?-qmSHP7keupPZhslKi9(ADwYE?GT#0U7E8G^6p>`2aK{8d5%o6(fDQq)uuR|gmK>O3HMF4?VP)__w0wXL=V?>3fdZ;4EFragk~e=XCFE;)=u>#>`vw>QDxHNc~O;uQGOqki0v0mOzmdAxCx|(d(`adZ|D>)CL?)qqv35WzTmVG7^dZf{BP~4hT6`~vT`9kZ>sg-4IcPLICIL099cjXNw+CU+<=4^4^(f|iSy_Rm$xg*e)$(izdky7(`VJsH;3o1drNZJ#B}iDRv<bB*MLrp*>KTS-@&e?lAWZ*5!PA5rRCEGC92BR|9skL#Um|h)JiHTCIE@8xsq~P4f^+|pf+8ltLALpw~eYSKNLa<o-%m50dLC!M)g~CzgXXWbg@<>wd)cz8nx>|4emjQ88j0Zq_Gl~Omd3A!ch_x5qcPeXvUHNU%}y0$+%XnyTbYN++cIz)lA)Hcw0j&H4dY9PcaL*>Sjh7og`WzB4=0`A#yLCEiyifZb79Lmu1GRDS+xZ`IK@jlwyjTP_)DITDF{OD?(X0M$)_Xm<{=gF2)MTJGzGN^nSlW4xL3Eok=Gj+Kg(AZ9}qe{gDD`weGdG{)BtO^?6VRv#R(=n)>t&$1;Lpc84+HZo|cCq|_Kg<f_CQu;0L|Ux*R84P%cI>KopJiN^~rFm_UjLAxmg8X%)vm(rwJ)tubq2Kj4J*Q8-h*0#mN+fFk_1Hp)=leA!^D>#V?hLN|JKwqJebQ|yWi9HPMnuOsKc9x~EhHSbK&Mza%XQVhKTELY1JR&EsaP7((wpU?>H{4Q8#K=MrYJbX%m3YGDAT>p<tmu$aYTm;~<TT9p!fGcRH!uDIwU0t$fWS=}WmvX0yDP5e-00-n8Ev`-LRqjGE}h{ZoTTL<$0G|46cKjC++2p5C2FIXNn41F)0qkNG?BBKreKs(OIRxYdxoXOM0wtaKcllfyviOvqEXlv(-e8)IK$tE5vtL2_fG`UO`0sq2xl%%3E|pD(4{PTi)z2jEhS+_E;@7r8p(K6`!*0aBhXu}q@8}=XU?PWw&(T^Z>5)Xz2280JXw_Ug?8CLGup%R`r*AG#>&Z=$#u~}9SJ)~%Uf@Re|7=d?lbmfH3$`<8JbV9?wx^Yg<;PY0Uok*N;mGhT^9&~-Fo&(VBcbeG(s1#{kjHr^V7hdgY;EI0BmbS*j^j#z5eSeLxv2Ly95jJbjfdxiE(K*?M_4`o~X|zcJ_d9k&rkvtY5HB6f99O*gvO#y5>MVGhrnUBoClN0<+z_7Ef4hWm6GU*B#$kllX#?QO)<g>bzaVU{?lYJ@(ZPDi%GqIq_XJ*!!B6_PYejb(a|l!8t}pK3YCd9ZylRQi`IH2w@AbA}N7n2-PG6nhR4E^NMkoU&Z8A`bt)_uAYc^o=jw|4eO*{2qA@n3@rL;@|f-KZ_e%q*27KlkmZ=f=KvD9yK}5C{J|hx4G=x70Lgk5=R3XwQKj`u(+^#rm8(UhdCgI+=7|V37Tj;o{qQbiQLHK}bR=i3!&sQqgvjN6qZO!lNK(}ZsZ}Sbw_jxOSNp1<IH#o-ceFvbZcxpQmBfn2R>)rFWaqHv6BQh9sjxtc5{PMx8QuT4OCgA53+6JK)(iy<DRhNn72QW#3Y-K`qas#?idrid8K7stix70eqybTyaUd(0Vd4O^8EjhkB_YyO+!b)TQ>7r8pSg@!qM^W3mPUJQzNl4QgXGX;q#F}0ZvlGj5JhCjmm(6!?cQqI*-leW^0nMx?Q5e!?Zkvvs$s8IybaSi1HJ$pn+jqywpK;tEb=$I`P>ww1swtlast&$Cbjwb`l~k$w$^F9?Wpvw3AdmC#)9r*lbrG71Hivt=gvrga?Jlm;<(Cs3;nFZdGBj0B6$=Ko+b!7kEgn-EG{V<PPz!Y6mIr2pl+B9{vwTIEP&Nk^?~%ZjE6t2a5YdJl~i!9vKXuj;~q8gdJRRZfJp;!ZLqB`HW}bO!g_B^il}5k^F?qik0==>p!Q2fgZIQ%UUR7s7|{Z>l!OiP3Pu)Td=tvLVX!9Oiq@!MX;Es?T?V|&u=+J64MOrL#ctLpb));4R&pcIX4;}Q5vX=T`KsVqmly0e;vpQjo?pxt-U`6Yf@Q6%W)$oA(Ar28Z<b8#$<wH-xf<jnu0el!f6a5MzsWGGfe;&Pq{=?Rk0m|sm%MZ9we{Di@?+CD<DmUbxV>1vp!}Q5uA0cL+y4L3KB=>eBZQPhs3U|I{*1QY7|Ma!#^$0P`^Lz2Gy4yiovhGOdC=9S(Enx6YOXS%YJG=w2A~uvbW?R*Jik=L#G)~Z(&=mlClb)QzpS=}zJxV4uJ0Q6?dFbizdHXhc0?k*p<mlYHh0vq`lCKuaS?2c35E^+L~#>rtmdj7G!aeQc@wqnmZ>U2<HjTEGVi+6bf|_duq!ez0^O~FJ#7O+ZJ4GqmpG<uHE{b8A8JQA@RS&R*{VKa6qYs|gnyzN+F&DN>9rC1wXk-AOh-p&9433`WpsnSIk0ah7(K!XI&fvo_a@9DVYQjIqR)<EhL<_ve@f{Wo1#URf%!<cv9BIJCJ!I8(7dwRy1gYqzG3b%H*Q|i5i2XLd4pT_SL=e<;H0J1*b0DrGp-vijcsd{@ajF$`gpXSsbl_;RB0xiHXp@LXXjUjR*SvH=*mjbwS5&*+VmX8uoA=YG((pRei-E8BYp5J3m5cBBw({RWH(#>w*SI+t_o6)SfGXC^WjjWbnDYYHIc4MKxGF}sn_eFqj=P$xSEDM%&(avMoUWjts2>Tyjq<Z<*T=DN}n?aRVj2kRtjCifx66f(d@!-jq_&rMO&-o{)tum6p#8VR*2a-OHC?(J;_IH2w*ahVtNy)QYE=6VW~km{AZwGfx!K)oJ6gP;1l*LBB?6+jO2&?3_sadly&Vox%^g$(aa?FXsJT`=`6m^x_;WWSbuA@W|y`xTIB$0_2Sg6FLk%a%!XyR&y~BCyuMF9I1Vb|a;6v)_Ivoac=(8yZE~1e!eaUDN8y(e{$_ajLz(|n!mF^<2Zwf(wj;R0_Fqp7w2FgyE}XAYj6X{5RzGCj5Lw63wzPMn<E>%K=p%<hCPB^bB`WwBh5c=xQA6d8Hnb}5lZ?{f4d@APf!l6DHj2UJ1Gc)mmb+Byn!+QTA_8C7Ob4a>GKpZX%)4J2!HV7zvG^9tE0%}>3PrKEK$8F_Wc#PD&yFAd%Nwe=Z_33!3(@1a1ggr1k{38+v?DAFkv~<1EJEpV+uRy#4OvbSnu16E66nViUY1|Mv!W_GhmykzR1xJIL+w9sEH{)df!jrkGDj6&bO<T3jWL?s2-5W0QM(~x20%uh>pe`)AF)zP#9iG_@5q6#NM&mop-FjcTxYO|(zwLgh-eqZ+F|8IUPFm>R``#73d^fc%q{_n&BTX)oZuE0NeSq5pijSKaz!rT*ma75Jwl3>g9FIXH8fl8_rPPkkwl$Uq!M(!Ods9v^&n)U825gceQ;a~qp$sKiW&Z);ZAHF!1>`ZeKGP66oeao0e_sqo;-xJ&FeqfAGX5STcO<y%+%|KETYxCWXt8_6Lx0A9nn69EhQ@p(w#~tO!?TZpQmu%=IR4NVwZ|MYf*5C&LEv~y;OM<cOX8S0(Y{G{#JKc2~q-Db<4@Ru>y}?y7A6VGre9*O1sjVGMS`$1bYiMD5f8w;M=agn<52i3ux*?!kfPBgE>3S@xXvSaH?#OL@Dv(+^{+r+@X}u=7k~F;0X*18sn;(2*!e}euJ9Y`OUZ?8ae8G(puLtLm$_9E%ZLK6cYNe+Eb+bX12$GQZMpGRknTWu4a+0v}T?5&8#nCShcQbQ&(Ws{{HUt{DL-hzXhVHQmAvE7!w4q&yGWpMW&A?%5OstT?;tC3ph5TeNliyCLF3-^uV4XS>$(?se~zIC&`bg@hhND+eg+qD{7bRBHG;rb>+S-_|dknOw4~ZZq)Zj%lNsXf_DA=O$Bbdif_ll6~cd~=6#FZWvtfUK-Ec5L!lj^uT?3Qy<bV!Q4{%Ka@|*K^B%A9eAqZW*>G5j?q6*HWjF4<NA#A?a@B-Bhon-!`Z`jUp;J}XvyjIne)<`;*SVF8YeU@=Hk9<}pYQasW0=iRmdNiPTJla*nJCGd3z!fM+hp8Cv@!F3MY;rtwu}zs3T}*A5FNnQm5S94(U*;CI4L0iKOD9#pE+4#Kv}%^_awR=+rt08vgxyFF+!A7+${Ex^L>Lx$Fy_|EVD^Yq<2EpIUd!lkiPIBinMc5Rq#t6l*_*a>O7ic=>YTY%M7&})MIYa82-W3d=hRMFQN>!8QjQK)@-s2EGi(N#ANBTjC48nS@`h30Nq(6zNm(^L8#n}yb+4gK|5#uvoh%#4BG6I9DagRaT(9mzqrz%afayRqG~~TA<H3(`v(+NWwVr)yrhK@<$u}tOIAi{okdh&T_>=jsp2x$%HKe@@C{XYdiZ#Q@2krk^m$ZX3jx<5Pai(&kNBXviN_L8N^v7XhM1|qx{NF9B13KeQTqIHXJHvHa~6ugznUnfd+t7iBO1eF?8}A%MrO3Mw;XJ{0~F<h#QaNR^v4`ttA%1apD~8=gdM0#_m!IqV+(lA=0;j37-HhpK84M;)JIYCdNrQQqZO#|SlsaQB^os*9kmnfoael-$RstV#1YbRC*iAjsTWsKSH_6)jc_`RgcBYuOMN3s<WZo4B!<8c`bJn5*`s1})j-+yV=?5<5GZSA)SV?!IX9=<`Uu!s=S02W&5|(Q;l<$_RHJXVsVsC$_>S~#5O}Bqh-Jy}17Gx6a9Ofis<TUUfqH!Iku%B(&n=0uHSebX2Yt)NJsrPXEU>W3y>v9g&aPa|^2aJ5FHXNd-#=s@WP%Zi=+QI0CG*AK#9iH4mNllccRpS6byi(vv8ugVP5Z4OlOEqHpHX>A8q?sdZ#k?}eCc<Ito8CK6<$`Uxm1Y;n=W`QcfHRs8rO6iKF7FfRVCB1HEtKz-06+i2v)?@>?|${qbKhd<7*UpaM4|<R>Kmi8vTE9-73d~(-!~@&jzK~pvGOlJ0|5kiSUm6Ty9=uC0I%URlUkY0T*2aYfoPLKBJccDbY}rB4}#WHSQ{j$RsAmI_0mABNd9GJKbbU;mtSDN)}O^u3Agbx%y|77E}eZYuEc!rEJ2MO2??%?Ol&Fbo{0uJj%!3e}q4;dAt~V`{Ju`Q|a$Ptks3SCO}nz{HE_3RM7P!F-ldcNiV3+4n*Z{THLZo=kS>7?M5t}N4YP7tb)s6fK}iIc$?Q4T72JQ?BzuYd;sjgYj}zBjxpD%1;*;gijHz6lgRvZ(kG!dkQtE%7FZK}T>CW0EG*+<jNf#2@jVbWrz(3l)rb={p<h7-pmgMIJxoO@5U-AkDvN({c>ebA+(8PCYU~Hcfi8Y&AoIcQd%qS!q8LqW)nGqj6?atP(m5r0*cF>GOS&rB3<Io31<>f%Tq-@s{k;>I=>F-+!A0BBaihd|Rqx)Q*zPB;9+=F7Mf$U~fXk2uy}rg@$CS{oDj<vc#|CQHWj&<C1&6`BMoH@<IU1!J(a^q%X=7qJB$6N?BdyN?t%nev%d4WJmi6rP_&9i7ThXH``46*#K+U_(z`n{W@g~W(Jp?1bUz77i7X6wGcyPFP@a^8ofs5)}QEeKORLsZvNqi^Fa`5M}YB67v>7ryHt~#vDb;IGaI(q7+0@g>Fhq1EWryD9{f`=*@@o`+aJl4bY_dH7n*J(Umcm4nQ@ccCR?)3Pe&IHc!zc0U4Xnm@Xp{pUs%m$ItCvMi$*PiJ{$FpJWu7AZlFNT77s<VDAS+?MOI>_fJW1{40U2%4Hcz6(8ygogB^WD+Oua{5#I1*p-o>ucU#K_S9`s>;(&*(}E2<jWK(Z}M33u$gZC0p$5?tUr-kU?b`z_p~KqQUE<li>XOlM|Rf$bsM1PCthVM^#CF&B{hDfvx@M>1}R(>h#uEdG^qo%movo`$0w~Fx5>918$b&TT{NSujp(q({q$!7MAK_)RZfyp7g65g7y=SPU&`A6K`C%7R2@1JIPGO7YD@Vpn6Vnj_V@5Gf=V7Pbc(|mB7wpi57AP*j0eNileQ`1(@xLdv8@;cdL%t8D)%WN~&*!s;pw}6!-fC^upT}(c2ofq8HwNe)RN49LNBcfu_hi&&Q(jPrWunua3P{Sizl!Dg<L?5#Z)m#cvxc$^OFm47M7K3|V-hwxeK&z%h!S-jJvY?^wd)Uy8-{>R7zVFv9ma&=B_r>e%G#iSd03ITkF8A3lafs$#-0`aGiTtMlQk@7Js;W9VjXu^wip!ha|~+l<ms#6jgZcYv$lbo>v(xW*5i6f7?@`*2)uU4@f$%~Mc*x&<j!g?Q{l_BCaS+++jvgVr4&@?+@uZFrVG{BKZuz?u<RHu`!uI*L?0aZNRRaWjAy4KxsiFdG>C-TUR5jB<XlD&Q51l>{_>c82LfqIjRa7*+FI@mr2%h~Z?`D2@k%S>B-Rn4eJ+vz4wq@%`#7kUsH8E81J1g+YHOe#qygaXCA@4M-8hhnxP;{kEO?C2hl~X45oM6SmA_uU9KgZ<gJ~Q63q?bU2v9<R$qv&~O7Q;rH-&+BBL9CA?&tj|?PjUvrG<27YiojbJZs3PZ!L>+cXxnWZbyPB&hGbWIDTZ_%%|QrZ$-XQ|L84A3SN6ntb1(}FZd5j%MH$b`rk3$!tY3-;Kg9Q&<hW@KDFPE1t|eGTq+ji+@;Yu2w^VHcQ&!zb(l^oIs(4q5Zet}-qOCDe+$_6Ia{_@E*7AiiQMFs0;LlIHXe%JW=B^Q>S?i{M-5%M4;1PV>c&*NO(crqP;6+4z-U70(2|=r(^?saG!xZhcV1tp{cx=^3#TbZ}?<rxMpK56hVdrkJk&dJNP=&iwvK&!XCI_}yh1X44}T6|H@ycXN9PD-Fm80T%2G0{pDK7X-NOLEwq@f~79*@C(g{w-J8o4!NS&`9I1Sj-C'


def ensure_internal_engine() -> None:
    """Installe automatiquement le moteur inclus dans cette application."""
    PLAYER.parent.mkdir(parents=True, exist_ok=True)
    engine_data = zlib.decompress(base64.b85decode(ENGINE_BUNDLE.encode("ascii")))

    try:
        current = PLAYER.read_bytes()
    except OSError:
        current = b""

    if current != engine_data:
        PLAYER.write_bytes(engine_data)
        PLAYER.chmod(0o755)


def find_script(video: Path) -> Path | None:
    # Priorité au funscript ORIGINAL placé dans le même dossier que la vidéo.
    candidates = [
        video.with_suffix(".funscript"),
        video.with_suffix(".vib.funscript"),
        SCRIPT_DIR / f"{video.stem}.funscript",
        SCRIPT_DIR / f"{video.stem}.vib.funscript",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def convertir_original_en_vibration_temporairement(
    script: Path,
    video: Path,
    amplification_percent: float = 0.0,
) -> Path:
    """
    Transforme le funscript linéaire en intensité de vibration par plateaux.

    Le fichier généré est temporaire :
      0 = arrêt, 1..100 = intensité de vibration.
    L'intensité dépend de la vitesse du mouvement du funscript original.

    Amplification :
      0 %   = calcul normal (x1)
      50 %  = environ x2
      100 % = environ x3
    """
    amplification_percent = max(0.0, min(100.0, float(amplification_percent)))
    amplification_factor = 1.0 + 2.0 * (amplification_percent / 100.0)

    donnees = json.loads(script.read_text(encoding="utf-8-sig"))
    actions_source = donnees.get("actions", [])
    actions = []

    for action in actions_source:
        try:
            at = max(0, int(action["at"]))
            pos = max(0, min(100, int(action["pos"])))
        except (KeyError, TypeError, ValueError):
            continue
        actions.append((at, pos))

    actions.sort(key=lambda item: item[0])
    if len(actions) < 2:
        raise ValueError("Le funscript original contient moins de deux actions valides.")

    # Éliminer les doublons de temps.
    uniques = []
    for action in actions:
        if uniques and uniques[-1][0] == action[0]:
            uniques[-1] = action
        else:
            uniques.append(action)

    sortie = [{"at": 0, "pos": 0}]

    def ajouter(at: int, pos: int) -> None:
        element = {"at": max(0, int(at)), "pos": max(0, min(100, int(pos)))}
        if sortie and sortie[-1]["at"] == element["at"]:
            sortie[-1] = element
        elif not sortie or sortie[-1] != element:
            sortie.append(element)

    for index in range(1, len(uniques)):
        debut, pos_debut = uniques[index - 1]
        fin, pos_fin = uniques[index]
        duree = fin - debut
        amplitude = abs(pos_fin - pos_debut)

        if duree <= 0:
            continue

        # Une longue section presque immobile devient un arrêt réel.
        if amplitude < 2 or (duree >= 2500 and amplitude < 8):
            commande = 0
        else:
            vitesse = amplitude * 1000.0 / duree
            vitesse_amplifiee = vitesse * amplification_factor
            # Minimum suffisamment élevé pour démarrer réellement le Mowgli.
            # L'amplification augmente la commande sans dépasser 100 %.
            puissance = max(0.20, min(1.0, vitesse_amplifiee / 160.0))
            commande = int(round(puissance * 100.0))

        ajouter(debut, commande)
        ajouter(fin, commande)

    ajouter(uniques[-1][0], 0)

    resultat = dict(donnees)
    resultat["actions"] = sortie
    resultat["inverted"] = False
    resultat["range"] = 100
    resultat["runtime_vibration_conversion"] = True
    resultat["runtime_amplification_percent"] = amplification_percent
    resultat["runtime_amplification_factor"] = amplification_factor

    destination = Path(tempfile.gettempdir()) / (
        f"vibration-runtime-{os.getpid()}-{video.stem}.vib.funscript"
    )
    destination.write_text(
        json.dumps(resultat, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return destination


def natural_key(path: Path) -> list[object]:
    return [
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", path.name)
    ]


def script_candidates_for_deletion(video: Path, selected_script: Path | None) -> list[Path]:
    """Retourne tous les scripts portant exactement le nom de la vidéo."""
    folders = [
        video.parent,
        video.parent / "rotation",
        video.parent / "Rotation",
        video.parent / "VibrationScript",
        SCRIPT_DIR,
    ]
    candidates: list[Path] = []
    if selected_script is not None:
        candidates.append(selected_script)
    for folder in folders:
        candidates.extend([
            folder / f"{video.stem}.funscript",
            folder / f"{video.stem}.vib.funscript",
        ])

    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = candidate.absolute()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(candidate)
    return unique


class VibrationPlayerGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1000x760")
        self.minsize(680, 480)
        self.configure(bg=COLORS["bg"])

        # Démarrer maximisé sous KDE/X11. Repli sur la taille de l'écran
        # lorsque le gestionnaire de fenêtres ne prend pas -zoomed en charge.
        try:
            self.attributes("-zoomed", True)
        except tk.TclError:
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        self.language = "fr"
        self.language_display = tk.StringVar(value="Français")
        self.video_path = tk.StringVar()
        self.script_path = tk.StringVar(value=self.t("Aucun script sélectionné"))
        self.status = tk.StringVar(value=self.t("Choisis une vidéo pour commencer."))
        self.max_power = tk.DoubleVar(value=1.00)
        self.zero_hold = tk.IntVar(value=150)
        self.smoothing = tk.DoubleVar(value=0.20)
        self.min_power = tk.DoubleVar(value=0.08)
        self.amplification = tk.DoubleVar(value=0.0)
        self.fullscreen = tk.BooleanVar(value=True)
        self.pump_enabled = tk.BooleanVar(value=False)
        self.pump_seconds = tk.DoubleVar(value=1.5)
        self.release_seconds = tk.DoubleVar(value=2.0)
        self.r4_interval_seconds = tk.DoubleVar(value=3.0)
        self.pause_min_seconds = tk.DoubleVar(value=12.0)
        self.pause_max_seconds = tk.DoubleVar(value=20.0)
        self.vibration_pattern = tk.StringVar(value="progressif3")
        self.vibration_pattern_2 = tk.StringVar(value="Aucun")
        self.vibration_pattern_3 = tk.StringVar(value="Aucun")
        self.random_patterns_enabled = tk.BooleanVar(value=False)
        self.delete_after_end_var = tk.BooleanVar(value=False)
        self.play_next_var = tk.BooleanVar(value=True)

        self.process: subprocess.Popen[str] | None = None
        self.playlist: list[Path] = []
        self.playlist_active = False
        self.delete_after_natural_end = False
        self.stop_requested = False
        self.manual_next_requested = False
        self.current_video: Path | None = None
        self.current_script: Path | None = None
        self.runtime_script: Path | None = None
        self.graph_actions: list[tuple[int, int]] = []
        self.graph_duration_ms = 0
        self.graph_position_ms = 0
        self.progress_file = Path(tempfile.gettempdir()) / f"vibration-player-progress-{os.getpid()}.json"
        self.mpv_socket = Path(tempfile.gettempdir()) / f"vibration-player-mpv-{os.getpid()}.sock"

        self.configure_styles()
        self.load_config()
        global LANGUAGE
        self.language = self.language if self.language in ("fr", "en") else "fr"
        LANGUAGE = self.language
        self.language_display.set("English" if self.language == "en" else "Français")
        # Refresh initial UI strings after the saved language has been loaded.
        self.script_path.set(self.t("Aucun script sélectionné"))
        self.status.set(self.t("Choisis une vidéo pour commencer."))
        if normalize_pattern(self.vibration_pattern_2.get()) == "Aucun":
            self.vibration_pattern_2.set(self.t("Aucun"))
        if normalize_pattern(self.vibration_pattern_3.get()) == "Aucun":
            self.vibration_pattern_3.set(self.t("Aucun"))
        try:
            ensure_internal_engine()
        except OSError:
            pass
        self.build_ui()
        self.after(150, self.update_graph_position)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def t(self, text: str) -> str:
        """Translate UI text using this window's selected language."""
        if self.language == "en":
            return TRANSLATIONS.get(text, text)
        return text

    def change_language(self, _event=None) -> None:
        global LANGUAGE
        selected = self.language_display.get()
        self.language = "en" if selected == "English" else "fr"
        LANGUAGE = self.language
        if normalize_pattern(self.vibration_pattern_2.get()) == "Aucun":
            self.vibration_pattern_2.set(self.t("Aucun"))
        if normalize_pattern(self.vibration_pattern_3.get()) == "Aucun":
            self.vibration_pattern_3.set(self.t("Aucun"))
        self.save_config()

        # Rebuild all visible widgets so every label/button immediately follows
        # the selected language without restarting the player.
        for child in list(self.winfo_children()):
            child.destroy()
        if not self.video_path.get():
            self.script_path.set(self.t("Aucun script sélectionné"))
            self.status.set(self.t("Choisis une vidéo pour commencer."))
        self.build_ui()

    def configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            ".",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            font=("Noto Sans", 10),
        )

        style.configure("Root.TFrame", background=COLORS["bg"])
        style.configure(
            "Card.TFrame",
            background=COLORS["panel"],
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Header.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            font=("Noto Sans", 22, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["muted"],
            font=("Noto Sans", 10),
        )
        style.configure(
            "CardTitle.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            font=("Noto Sans", 12, "bold"),
        )
        style.configure(
            "CardText.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["muted"],
        )
        style.configure(
            "Value.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["accent_hover"],
            font=("Noto Sans", 10, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background=COLORS["panel_alt"],
            foreground=COLORS["muted"],
            padding=(12, 9),
        )

        # High-contrast controls for dark themes.
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["panel_alt"],
            background=COLORS["panel_alt"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["text"],
            bordercolor=COLORS["accent"],
            lightcolor=COLORS["accent"],
            darkcolor=COLORS["accent"],
            padding=7,
        )
        style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", COLORS["panel_alt"]),
                ("disabled", COLORS["panel"]),
            ],
            foreground=[
                ("readonly", COLORS["text"]),
                ("disabled", COLORS["muted"]),
            ],
            selectbackground=[("readonly", COLORS["accent"])],
            selectforeground=[("readonly", "#ffffff")],
        )
        style.configure(
            "Dark.TCheckbutton",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            indicatorcolor=COLORS["panel_alt"],
            padding=(2, 5),
        )
        style.map(
            "Dark.TCheckbutton",
            background=[("active", COLORS["panel"])],
            foreground=[("active", "#ffffff"), ("disabled", COLORS["muted"])],
            indicatorcolor=[
                ("selected", COLORS["accent"]),
                ("!selected", COLORS["panel_alt"]),
            ],
        )

        style.configure(
            "Dark.TEntry",
            fieldbackground=COLORS["panel_alt"],
            foreground=COLORS["text"],
            insertcolor=COLORS["text"],
            bordercolor=COLORS["border"],
            padding=9,
        )
        style.map(
            "Dark.TEntry",
            fieldbackground=[("readonly", COLORS["panel_alt"])],
            foreground=[("readonly", COLORS["text"])],
        )

        style.configure(
            "Accent.TButton",
            background=COLORS["accent"],
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            padding=(16, 11),
            font=("Noto Sans", 10, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[
                ("active", COLORS["accent_hover"]),
                ("disabled", COLORS["panel_alt"]),
            ],
            foreground=[("disabled", "#6e7582")],
        )

        style.configure(
            "Secondary.TButton",
            background=COLORS["panel_alt"],
            foreground=COLORS["text"],
            borderwidth=1,
            padding=(14, 10),
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#2a2f39")],
        )

        style.configure(
            "Danger.TButton",
            background="#382028",
            foreground="#ff8797",
            borderwidth=0,
            padding=(14, 10),
            font=("Noto Sans", 10, "bold"),
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#4a2530")],
        )

        style.configure(
            "Dark.Horizontal.TScale",
            background=COLORS["panel"],
            troughcolor=COLORS["track"],
            bordercolor=COLORS["panel"],
            lightcolor=COLORS["accent"],
            darkcolor=COLORS["accent"],
        )

        style.configure(
            "Dark.TCheckbutton",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            indicatorbackground=COLORS["panel_alt"],
            indicatorforeground=COLORS["accent"],
            padding=4,
        )
        style.map(
            "Dark.TCheckbutton",
            background=[("active", COLORS["panel"])],
            foreground=[("active", COLORS["text"])],
        )

    def build_ui(self) -> None:
        # Zone défilable : aucun contrôle ne reste caché lorsque la mise à
        # l'échelle KDE est élevée ou que la fenêtre est réduite.
        shell = ttk.Frame(self, style="Root.TFrame")
        self.ui_shell = shell
        shell.pack(fill="both", expand=True)

        # Bande funscript toujours visible au bas de la fenêtre.
        graph_frame = tk.Frame(
            shell,
            bg="#050609",
            height=110,
            highlightbackground="#3b4050",
            highlightthickness=1,
        )
        graph_frame.pack(side="bottom", fill="x")
        graph_frame.pack_propagate(False)

        graph_header = tk.Frame(graph_frame, bg="#050609", height=28)
        graph_header.pack(side="top", fill="x")
        graph_header.pack_propagate(False)

        graph_title = tk.Label(
            graph_header,
            text=self.t("VIBRATION FUNSCRIPT — clique ou glisse pour déplacer la vidéo"),
            bg="#050609",
            fg="#aeb6c5",
            font=("Noto Sans", 8, "bold"),
            anchor="w",
            padx=10,
        )
        graph_title.pack(side="left", fill="x", expand=True)

        for label, command in (
            ("−10 s", lambda: self.seek_relative(-10)),
            ("Pause / Reprendre", self.toggle_pause),
            ("+10 s", lambda: self.seek_relative(10)),
        ):
            tk.Button(
                graph_header,
                text=self.t(label),
                command=command,
                bg="#20242d",
                fg="#f2f4f8",
                activebackground="#353b49",
                activeforeground="#ffffff",
                relief="flat",
                borderwidth=0,
                padx=10,
                pady=2,
                cursor="hand2",
                font=("Noto Sans", 8, "bold"),
            ).pack(side="left", padx=(0, 4), pady=3)

        self.graph_canvas = tk.Canvas(
            graph_frame,
            bg="#090b10",
            highlightthickness=0,
            borderwidth=0,
            height=86,
        )
        self.graph_canvas.pack(side="bottom", fill="both", expand=True)
        self.graph_canvas.bind(
            "<Configure>",
            lambda _event: self.draw_funscript_graph()
        )
        self.graph_canvas.bind("<Button-1>", self.seek_from_graph)
        self.graph_canvas.bind("<B1-Motion>", self.seek_from_graph)
        self.graph_canvas.bind("<Button-3>", self.toggle_pause)
        self.graph_canvas.bind("<MouseWheel>", self.graph_mousewheel)
        self.graph_canvas.bind("<Button-4>", self.graph_mousewheel)
        self.graph_canvas.bind("<Button-5>", self.graph_mousewheel)

        content_frame = ttk.Frame(shell, style="Root.TFrame")
        content_frame.pack(side="top", fill="both", expand=True)
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=1)

        canvas = tk.Canvas(
            content_frame,
            bg=COLORS["bg"],
            highlightthickness=0,
            borderwidth=0,
        )
        scrollbar = ttk.Scrollbar(
            content_frame,
            orient="vertical",
            command=canvas.yview
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        root = ttk.Frame(canvas, style="Root.TFrame", padding=24)
        root.columnconfigure(0, weight=1)
        window_id = canvas.create_window((0, 0), window=root, anchor="nw")

        def update_scrollregion(_event=None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def fit_width(event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        def mousewheel(event) -> None:
            if getattr(event, "delta", 0):
                canvas.yview_scroll(int(-event.delta / 120), "units")
            elif getattr(event, "num", None) == 4:
                canvas.yview_scroll(-3, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(3, "units")

        root.bind("<Configure>", update_scrollregion)
        canvas.bind("<Configure>", fit_width)
        canvas.bind_all("<MouseWheel>", mousewheel)
        canvas.bind_all("<Button-4>", mousewheel)
        canvas.bind_all("<Button-5>", mousewheel)

        # F11 bascule l'application en plein écran; Échap revient maximisé.
        self.bind("<F11>", self.toggle_app_fullscreen)
        self.bind("<Escape>", self.leave_app_fullscreen)

        header = ttk.Frame(root, style="Root.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header, text="JoyHub Melody Player", style="Header.TLabel"
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text=APP_VERSION,
            style="Subtitle.TLabel",
        ).grid(row=0, column=1, rowspan=2, sticky="ne", padx=(20, 0))
        self.language_combo = ttk.Combobox(
            header,
            textvariable=self.language_display,
            values=("Français", "English"),
            state="readonly",
            width=10,
        )
        self.language_combo.grid(row=0, column=2, rowspan=2, sticky="ne", padx=(10, 0))
        self.language_combo.bind("<<ComboboxSelected>>", self.change_language)
        ttk.Label(
            header,
            text=self.t("JoyHub Melody BLE direct — connexion mémorisée + schémas vibration + R4"),
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        file_card = ttk.Frame(root, style="Card.TFrame", padding=18)
        file_card.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        file_card.columnconfigure(1, weight=1)

        ttk.Label(
            file_card, text=self.t("Sélection"), style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        ttk.Label(
            file_card, text=self.t("Vidéo"), style="CardText.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=6)

        ttk.Entry(
            file_card,
            textvariable=self.video_path,
            state="readonly",
            style="Dark.TEntry",
        ).grid(row=1, column=1, sticky="ew", padx=10, pady=6)

        ttk.Button(
            file_card,
            text=self.t("Parcourir"),
            style="Secondary.TButton",
            command=self.choose_video,
        ).grid(row=1, column=2, pady=6)

        ttk.Label(
            file_card, text=self.t("Script"), style="CardText.TLabel"
        ).grid(row=2, column=0, sticky="nw", pady=6)

        self.script_label = ttk.Label(
            file_card,
            textvariable=self.script_path,
            style="CardText.TLabel",
            wraplength=580,
        )
        self.script_label.grid(
            row=2, column=1, columnspan=2, sticky="w", padx=10, pady=6
        )

        settings = ttk.Frame(root, style="Card.TFrame", padding=18)
        settings.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        settings.columnconfigure(1, weight=1)

        ttk.Label(
            settings, text=self.t("Réglages"), style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        self.add_scale(
            settings, 1, "Vibration maximale", self.max_power, 0.10, 1.00,
            lambda v: f"{float(v) * 100:.0f} %"
        )
        self.add_scale(
            settings, 2, "Maintien à zéro", self.zero_hold, 0, 1000,
            lambda v: f"{int(float(v))} ms"
        )
        self.add_scale(
            settings, 3, "Lissage", self.smoothing, 0.00, 0.95,
            lambda v: f"{float(v):.2f}"
        )
        self.add_scale(
            settings, 4, "Vibration minimale", self.min_power, 0.00, 0.50,
            lambda v: f"{float(v) * 100:.0f} %"
        )
        self.add_scale(
            settings, 5, "Amplification vibration", self.amplification, 0, 100,
            lambda v: (
                f"{float(v):.0f} %  "
                f"(x{1.0 + 2.0 * float(v) / 100.0:.2f})"
            )
        )

        ttk.Checkbutton(
            settings,
            text=self.t("Ouvrir MPV en plein écran sur l’écran de droite"),
            variable=self.fullscreen,
            style="Dark.TCheckbutton",
        ).grid(row=6, column=1, sticky="w", padx=10, pady=(10, 2))

        ttk.Checkbutton(
            settings,
            text=self.t("Activer le contrôle PUMP / R4 (CONSTRICT)"),
            variable=self.pump_enabled,
            style="Dark.TCheckbutton",
        ).grid(row=7, column=1, sticky="w", padx=10, pady=(8, 8))

        ttk.Label(
            settings, text=self.t("Contrôle PUMP / R4"), style="CardTitle.TLabel"
        ).grid(row=8, column=0, columnspan=3, sticky="w", pady=(12, 8))

        self.add_scale(
            settings, 9, "Durée du PUMP", self.pump_seconds, 0.50, 5.00,
            lambda v: f"{float(v):.1f} s"
        )

        self.add_scale(
            settings, 10, "Durée du relâchement", self.release_seconds, 0.50, 8.00,
            lambda v: f"{float(v):.1f} s"
        )

        self.add_scale(
            settings, 11, "R4 répété toutes les", self.r4_interval_seconds, 0.50, 10.00,
            lambda v: f"{float(v):.1f} s"
        )

        self.add_scale(
            settings, 12, "Pause minimale entre PUMP", self.pause_min_seconds, 2.0, 60.0,
            lambda v: f"{float(v):.0f} s"
        )

        self.add_scale(
            settings, 13, "Pause maximale entre PUMP", self.pause_max_seconds, 2.0, 90.0,
            lambda v: f"{float(v):.0f} s"
        )

        ttk.Label(
            settings, text=self.t("Schéma vibration 1"), style="CardText.TLabel"
        ).grid(row=14, column=0, sticky="w", pady=(12, 6))

        self.pattern_combo = ttk.Combobox(
            settings,
            textvariable=self.vibration_pattern,
            state="readonly",
            values=VIBRATION_PATTERN_NAMES,
            width=30,
        )
        self.pattern_combo.grid(row=14, column=1, sticky="w", padx=10, pady=(12, 6))

        ttk.Label(
            settings, text=self.t("Schéma vibration 2"), style="CardText.TLabel"
        ).grid(row=15, column=0, sticky="w", pady=6)

        self.pattern_combo_2 = ttk.Combobox(
            settings,
            textvariable=self.vibration_pattern_2,
            state="readonly",
            values=(self.t("Aucun"),) + VIBRATION_PATTERN_NAMES,
            width=30,
        )
        self.pattern_combo_2.grid(row=15, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(
            settings, text=self.t("Schéma vibration 3"), style="CardText.TLabel"
        ).grid(row=16, column=0, sticky="w", pady=6)

        self.pattern_combo_3 = ttk.Combobox(
            settings,
            textvariable=self.vibration_pattern_3,
            state="readonly",
            values=(self.t("Aucun"),) + VIBRATION_PATTERN_NAMES,
            width=30,
        )
        self.pattern_combo_3.grid(row=16, column=1, sticky="w", padx=10, pady=6)

        ttk.Checkbutton(
            settings,
            text=self.t("Choisir aléatoirement parmi les 1 à 3 schémas sélectionnés"),
            variable=self.random_patterns_enabled,
            style="Dark.TCheckbutton",
        ).grid(row=17, column=1, sticky="w", padx=10, pady=(6, 2))

        ttk.Checkbutton(
            settings,
            text=self.t("Supprimer la vidéo et ses funscripts à la fin ou en passant à la suivante"),
            variable=self.delete_after_end_var,
            style="Dark.TCheckbutton",
        ).grid(row=18, column=1, sticky="w", padx=10, pady=(8, 2))

        ttk.Checkbutton(
            settings,
            text=self.t("Passer automatiquement à la vidéo suivante"),
            variable=self.play_next_var,
            style="Dark.TCheckbutton",
        ).grid(row=19, column=1, sticky="w", padx=10, pady=(6, 2))

        actions = ttk.Frame(root, style="Root.TFrame")
        actions.grid(row=3, column=0, sticky="ew", pady=(0, 14))
        actions.columnconfigure(0, weight=1)

        self.launch_button = ttk.Button(
            actions,
            text=self.t("▶  Lancer la vidéo"),
            command=self.launch,
            state="disabled",
            style="Accent.TButton",
        )
        self.launch_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.folder_button = ttk.Button(
            actions,
            text=self.t("⏭  Lire le dossier"),
            command=self.launch_folder_playlist,
            state="disabled",
            style="Secondary.TButton",
        )
        self.folder_button.grid(row=0, column=1, padx=(0, 8))

        self.next_button = ttk.Button(
            actions,
            text=self.t("⏩  Vidéo suivante"),
            command=self.next_video,
            state="disabled",
            style="Secondary.TButton",
        )
        self.next_button.grid(row=0, column=2, padx=(0, 8))

        ttk.Button(
            actions,
            text=self.t("🧪  Test aspiration Melody 10 s"),
            command=self.test_pump,
            style="Secondary.TButton",
        ).grid(row=0, column=3, padx=(0, 8))

        ttk.Button(
            actions,
            text=self.t("■  Arrêter"),
            command=self.stop,
            style="Danger.TButton",
        ).grid(row=0, column=4)

        self.status_label = ttk.Label(
            root,
            textvariable=self.status,
            style="Status.TLabel",
            anchor="w",
        )
        self.status_label.grid(row=4, column=0, sticky="ew")

        self.after(100, self.draw_funscript_graph)

    def clear_funscript_graph(self) -> None:
        self.graph_actions = []
        self.graph_duration_ms = 0
        self.graph_position_ms = 0
        if hasattr(self, "graph_canvas"):
            self.draw_funscript_graph()

    def load_funscript_graph(self, script: Path) -> None:
        try:
            data = json.loads(script.read_text(encoding="utf-8-sig"))
            actions = data.get("actions", [])
            parsed = []
            for action in actions:
                at = int(action.get("at", 0))
                pos = max(0, min(100, int(action.get("pos", 50))))
                parsed.append((at, pos))
            parsed.sort()
            self.graph_actions = parsed
            self.graph_duration_ms = parsed[-1][0] if parsed else 0
            self.graph_position_ms = 0
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.graph_actions = []
            self.graph_duration_ms = 0
            self.graph_position_ms = 0
        if hasattr(self, "graph_canvas"):
            self.draw_funscript_graph()

    def draw_funscript_graph(self) -> None:
        if not hasattr(self, "graph_canvas"):
            return
        c = self.graph_canvas
        c.delete("all")
        w = max(c.winfo_width(), 2)
        h = max(c.winfo_height(), 2)
        # Grille très visible, même avant le chargement d'un script.
        for fraction in (0.25, 0.50, 0.75):
            y_grid = h * fraction
            c.create_line(
                0, y_grid, w, y_grid,
                fill="#262b36",
                width=1,
                dash=(3, 5),
            )
        for fraction in (0.25, 0.50, 0.75):
            x_grid = w * fraction
            c.create_line(
                x_grid, 0, x_grid, h,
                fill="#171b23",
                width=1,
            )

        duration = self.graph_duration_ms
        if self.graph_actions and duration > 0:
            points = []
            for at, pos in self.graph_actions:
                x = (at / duration) * w
                y = h - 5 - (pos / 100.0) * (h - 10)
                points.extend((x, y))
            if len(points) >= 4:
                c.create_line(
                    *points,
                    fill="#b39cff",
                    width=2,
                    smooth=False,
                )

            x_cursor = (
                min(max(self.graph_position_ms / duration, 0.0), 1.0) * w
            )
            c.create_line(
                x_cursor, 0, x_cursor, h,
                fill="#ff263f",
                width=4,
            )
        else:
            c.create_text(
                12,
                h / 2,
                text=self.t("Choisis une vidéo avec son funscript"),
                fill="#c4cad6",
                anchor="w",
                font=("Noto Sans", 10, "bold"),
            )
            c.create_line(
                3, 0, 3, h,
                fill="#ff263f",
                width=4,
            )

    def send_mpv_command(self, command: list) -> bool:
        """Envoie une commande JSON IPC au MPV actuellement lancé."""
        if self.process is None or self.process.poll() is not None:
            self.set_status(self.t("Aucune vidéo en lecture."), "warning")
            return False
        if not self.mpv_socket.exists():
            self.set_status(self.t("Contrôle MPV indisponible : socket IPC absent."), "danger")
            return False
        payload = json.dumps({"command": command}).encode("utf-8") + b"\n"
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.settimeout(0.5)
                client.connect(str(self.mpv_socket))
                client.sendall(payload)
            return True
        except OSError as exc:
            self.set_status((f"MPV control error: {exc}" if LANGUAGE == "en" else f"Erreur de contrôle MPV : {exc}"), "danger")
            return False

    def seek_relative(self, seconds: float) -> None:
        self.send_mpv_command(["seek", float(seconds), "relative+exact"])

    def toggle_pause(self, _event=None):
        self.send_mpv_command(["cycle", "pause"])
        return "break"

    def seek_from_graph(self, event):
        duration_ms = self.graph_duration_ms
        width = max(self.graph_canvas.winfo_width(), 1)
        if duration_ms <= 0:
            self.set_status(self.t("Durée de la vidéo inconnue."), "warning")
            return "break"
        ratio = min(max(event.x / width, 0.0), 1.0)
        seconds = (duration_ms * ratio) / 1000.0
        if self.send_mpv_command(["seek", seconds, "absolute+exact"]):
            self.graph_position_ms = int(seconds * 1000)
            self.draw_funscript_graph()
        return "break"

    def graph_mousewheel(self, event):
        if getattr(event, "num", None) == 4 or getattr(event, "delta", 0) > 0:
            self.seek_relative(5)
        else:
            self.seek_relative(-5)
        return "break"

    def update_graph_position(self) -> None:
        if self.process is not None and self.process.poll() is None:
            try:
                data = json.loads(
                    self.progress_file.read_text(encoding="utf-8")
                )
                self.graph_position_ms = int(
                    float(data.get("time_pos", 0.0)) * 1000
                )
                duration_ms = int(
                    float(data.get("duration", 0.0)) * 1000
                )
                if duration_ms > 0:
                    self.graph_duration_ms = duration_ms
                self.draw_funscript_graph()
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                pass

        # La boucle continue même avant ou après une lecture.
        self.after(80, self.update_graph_position)

    def add_scale(
        self, parent, row, label, variable, minimum, maximum, formatter
    ) -> None:
        ttk.Label(
            parent, text=self.t(label), style="CardText.TLabel"
        ).grid(row=row, column=0, sticky="w", pady=8)

        scale = ttk.Scale(
            parent,
            variable=variable,
            from_=minimum,
            to=maximum,
            orient="horizontal",
            style="Dark.Horizontal.TScale",
        )
        scale.grid(row=row, column=1, sticky="ew", padx=10, pady=8)

        value_label = ttk.Label(
            parent, width=9, anchor="e", style="Value.TLabel"
        )
        value_label.grid(row=row, column=2, sticky="e")

        def update(*_) -> None:
            value_label.configure(text=formatter(variable.get()))

        variable.trace_add("write", update)
        update()

    def set_status(self, text: str, kind: str = "neutral") -> None:
        colors = {
            "neutral": COLORS["muted"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "danger": COLORS["danger"],
        }
        self.status.set(text)
        ttk.Style(self).configure(
            "Status.TLabel",
            background=COLORS["panel_alt"],
            foreground=colors.get(kind, COLORS["muted"]),
            padding=(12, 9),
        )

    def toggle_app_fullscreen(self, _event=None) -> None:
        enabled = bool(self.attributes("-fullscreen"))
        self.attributes("-fullscreen", not enabled)

    def leave_app_fullscreen(self, _event=None) -> None:
        if bool(self.attributes("-fullscreen")):
            self.attributes("-fullscreen", False)
        try:
            self.attributes("-zoomed", True)
        except tk.TclError:
            pass

    def choose_video(self) -> None:
        initial = VIDEO_DIR if VIDEO_DIR.is_dir() else Path.home()
        chosen = filedialog.askopenfilename(
            title=self.t("Choisir une vidéo"),
            initialdir=str(initial),
            filetypes=((self.t("Vidéos"), "*.mp4 *.mkv *.avi *.mov *.webm *.m4v"), (self.t("Tous les fichiers"), "*")),
        )
        if not chosen:
            return

        video = Path(chosen)
        script = find_script(video)
        self.video_path.set(str(video))

        if script:
            self.load_funscript_graph(script)
            self.script_path.set(f"✓  {script}")
            self.script_label.configure(foreground=COLORS["success"])
            self.set_status(self.t("Funscript original trouvé. Conversion vibration automatique prête."), "success")
            self.launch_button.configure(state="normal")
            self.folder_button.configure(state="normal")
            self.next_button.configure(state="normal")
        else:
            self.clear_funscript_graph()
            self.script_path.set(
                (f"✕  No matching script in {SCRIPT_DIR}" if LANGUAGE == "en" else f"✕  Aucun script correspondant dans {SCRIPT_DIR}")
            )
            self.script_label.configure(foreground=COLORS["danger"])
            self.set_status(self.t("Aucun MelodyScript correspondant."), "danger")
            self.launch_button.configure(state="disabled")
            self.folder_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
            messagebox.showwarning(
                self.t("MelodyScript introuvable"),
                (
                    "No funscript with the same base name as the video was found.\n\n"
                    f"Folder searched:\n{SCRIPT_DIR}\n\n"
                    f"Names searched:\n{video.stem}.vib.funscript\n{video.stem}.funscript"
                    if LANGUAGE == "en" else
                    "Aucun funscript portant le même nom que la vidéo n'a été trouvé.\n\n"
                    f"Dossier recherché :\n{SCRIPT_DIR}\n\n"
                    f"Noms recherchés :\n{video.stem}.vib.funscript\n{video.stem}.funscript"
                ),
            )


    def test_pump(self) -> None:
        """Lance un test direct sans vidéo et sans funscript."""
        if not PYTHON.is_file():
            messagebox.showerror(
                self.t("Python introuvable"),
                (f"Python environment not found:\n{PYTHON}" if LANGUAGE == "en" else f"Environnement Python introuvable :\n{PYTHON}")
            )
            return

        try:
            ensure_internal_engine()
        except OSError as exc:
            messagebox.showerror(
                self.t("Erreur du moteur intégré"),
                (f"Unable to prepare the test engine:\n{exc}" if LANGUAGE == "en" else f"Impossible de préparer le moteur de test :\n{exc}")
            )
            return

        self.stop()

        command = [
            str(PYTHON),
            str(PLAYER),
            "--test-pump",
            "--test-pump-seconds", "10",
            "--device", "JoyHub Melody",
            "--max-power", f"{self.max_power.get():.3f}",
            "--verbose",
            "--progress-file", str(self.progress_file),
        ]

        try:
            self.process = subprocess.Popen(command)
        except OSError as exc:
            messagebox.showerror(self.t("Erreur de lancement"), str(exc))
            return

        self.set_status(
            (f"Melody suction test running for 10 seconds — PID {self.process.pid}" if LANGUAGE == "en" else f"Test aspiration Melody en cours pendant 10 secondes — PID {self.process.pid}"),
            "warning",
        )
        self.after(100, self.check_process)


    def launch(self, video: Path | None = None, script: Path | None = None) -> None:
        if video is None:
            video = Path(self.video_path.get())
        if script is None:
            script_text = self.script_path.get().removeprefix("✓  ")
            script = Path(script_text)

        if not video.is_file() or not script.is_file():
            messagebox.showerror(
                self.t("Fichier introuvable"),
                self.t("La vidéo ou le MelodyScript n'existe plus.")
            )
            return

        if not PYTHON.is_file():
            messagebox.showerror(
                self.t("Python introuvable"),
                (f"Python environment not found:\n{PYTHON}" if LANGUAGE == "en" else f"Environnement Python introuvable :\n{PYTHON}")
            )
            return

        try:
            ensure_internal_engine()
        except OSError as exc:
            messagebox.showerror(
                self.t("Erreur du moteur intégré"),
                (f"Unable to prepare the playback engine:\n{exc}" if LANGUAGE == "en" else f"Impossible de préparer le moteur de lecture :\n{exc}")
            )
            return

        if not self.playlist_active:
            self.stop()
        self.stop_requested = False
        self.current_video = video
        self.current_script = script

        # Conversion automatique au lancement : la vitesse du mouvement
        # du funscript devient une intensité de vibration 0..100.
        try:
            runtime_script = convertir_original_en_vibration_temporairement(
                script,
                video,
                self.amplification.get(),
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            messagebox.showerror(
                self.t("Erreur de conversion"),
                (f"Unable to convert the original funscript to vibration:\n{exc}" if LANGUAGE == "en" else f"Impossible de convertir le funscript original en vibration :\n{exc}"),
            )
            return

        self.runtime_script = runtime_script
        self.load_funscript_graph(runtime_script)
        try:
            self.progress_file.unlink(missing_ok=True)
            self.mpv_socket.unlink(missing_ok=True)
        except OSError:
            pass
        self.save_config()

        command = [
            str(PYTHON),
            str(PLAYER),
            str(video),
            str(runtime_script),
            "--max-power", f"{self.max_power.get():.3f}",
            "--zero-hold-ms", str(int(self.zero_hold.get())),
            "--speed-smoothing", f"{self.smoothing.get():.3f}",
            "--min-running-power", f"{self.min_power.get():.3f}",
            "--min-change", "0.001",
            "--device", "JoyHub Melody",
            "--scan-seconds", "1.0",
            "--verbose",
            "--progress-file", str(self.progress_file),
            f"--mpv-arg=--input-ipc-server={self.mpv_socket}",
            "--mpv-arg=--screen=1",
            "--mpv-arg=--fs-screen=1",
        ]

        if self.pump_enabled.get():
            command.extend([
                "--pump",
                "--pump-seconds", f"{self.pump_seconds.get():.2f}",
                "--release-seconds", f"{self.release_seconds.get():.2f}",
                "--r4-interval", f"{self.r4_interval_seconds.get():.2f}",
                "--pause-min", f"{min(self.pause_min_seconds.get(), self.pause_max_seconds.get()):.2f}",
                "--pause-max", f"{max(self.pause_min_seconds.get(), self.pause_max_seconds.get()):.2f}",
                "--vibration-pattern", self.vibration_pattern.get(),
                "--vibration-pattern-2", normalize_pattern(self.vibration_pattern_2.get()),
                "--vibration-pattern-3", normalize_pattern(self.vibration_pattern_3.get()),
            ])
            if self.random_patterns_enabled.get():
                command.append("--random-vibration-patterns")

        if self.fullscreen.get():
            command.append("--mpv-arg=--fs")

        try:
            self.process = subprocess.Popen(command)
        except OSError as exc:
            messagebox.showerror(self.t("Erreur de lancement"), str(exc))
            return

        if LANGUAGE == "en":
            pump_text = (
                f" — PUMP {self.pump_seconds.get():.1f}s / R4 {self.r4_interval_seconds.get():.1f}s / pause {self.pause_min_seconds.get():.0f}-{self.pause_max_seconds.get():.0f}s / pattern {self.vibration_pattern.get()}"
                if self.pump_enabled.get() else " — pumping disabled"
            )
        else:
            pump_text = (
                f" — PUMP {self.pump_seconds.get():.1f}s / R4 {self.r4_interval_seconds.get():.1f}s / pause {self.pause_min_seconds.get():.0f}-{self.pause_max_seconds.get():.0f}s / motif {self.vibration_pattern.get()}"
                if self.pump_enabled.get() else " — pompage désactivé"
            )
        amplification_factor = 1.0 + 2.0 * self.amplification.get() / 100.0
        amplification_text = (
            (f" — amplification {self.amplification.get():.0f} % " if LANGUAGE == "fr" else f" — amplification {self.amplification.get():.0f}% ")
            + f"(x{amplification_factor:.2f})"
        )
        self.set_status(
            ((f"Playing: {video.name}" if LANGUAGE == "en" else f"Lecture en cours : {video.name}")
             + pump_text + amplification_text + f" — PID {self.process.pid}"),
            "success",
        )
        self.after(100, self.check_process)

    def next_video(self) -> None:
        video = self.current_video
        script = self.current_script

        if video is None:
            selected_text = self.video_path.get().strip()
            if selected_text:
                selected = Path(selected_text)
                if selected.is_file():
                    video = selected
                    script = find_script(selected)

        if video is None or not video.is_file():
            self.set_status(self.t("Aucune vidéo actuelle à passer."), "warning")
            return

        # Préparer les vidéos suivantes si aucune liste n'est active.
        if not self.playlist_active:
            videos = sorted(
                [
                    path for path in video.parent.iterdir()
                    if path.is_file()
                    and path.suffix.casefold() in VIDEO_EXTENSIONS
                ],
                key=natural_key,
            )
            try:
                current_index = videos.index(video)
            except ValueError:
                self.set_status(
                    self.t("La vidéo actuelle n’est plus dans son dossier."),
                    "warning",
                )
                return

            self.playlist = [
                candidate
                for candidate in videos[current_index + 1:]
                if find_script(candidate)
            ]
            self.playlist_active = bool(self.playlist)

        deleted_count = 0
        if self.delete_after_end_var.get():
            deleted_count = len(self.delete_completed_files(video, script))

        if not self.playlist:
            self.playlist_active = False
            if self.process is not None and self.process.poll() is None:
                self.stop_requested = True
                self.process.terminate()

            if deleted_count:
                self.set_status(
                    ((f"{video.name} deleted ({deleted_count} file(s)). No next video." if LANGUAGE == "en"
                      else f"{video.name} supprimée ({deleted_count} fichier(s)). Aucune vidéo suivante.")),
                    "success",
                )
            else:
                self.set_status(self.t("Aucune vidéo suivante disponible."), "warning")
            return

        self.manual_next_requested = True
        self.stop_requested = False

        if deleted_count:
            self.set_status(
                ((f"{video.name} deleted ({deleted_count} file(s)). Moving to the next…" if LANGUAGE == "en"
                  else f"{video.name} supprimée ({deleted_count} fichier(s)). Passage à la suivante…")),
                "success",
            )
        else:
            self.set_status(self.t("Passage à la vidéo suivante…"), "neutral")

        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
        else:
            self.manual_next_requested = False
            self.current_video = None
            self.current_script = None
            self.after(50, self.play_next_in_playlist)

    def launch_folder_playlist(self) -> None:
        """Lit la vidéo choisie puis toutes les suivantes du même dossier."""
        selected = Path(self.video_path.get())
        if not selected.is_file():
            messagebox.showerror(self.t("Vidéo introuvable"), self.t("Choisis d’abord une vidéo valide."))
            return

        videos = sorted(
            [
                path for path in selected.parent.iterdir()
                if path.is_file() and path.suffix.casefold() in VIDEO_EXTENSIONS
            ],
            key=natural_key,
        )
        try:
            start_index = videos.index(selected)
        except ValueError:
            messagebox.showerror(self.t("Erreur"), self.t("La vidéo sélectionnée n’est plus dans le dossier."))
            return

        playlist = [video for video in videos[start_index:] if find_script(video)]
        if not playlist:
            messagebox.showwarning(
                self.t("Aucune vidéo lisible"),
                self.t("Aucune vidéo à partir de la sélection ne possède un funscript correspondant."),
            )
            return

        self.stop()
        self.playlist = playlist
        self.playlist_active = True
        self.delete_after_natural_end = self.delete_after_end_var.get()
        self.stop_requested = False
        self.play_next_in_playlist()

    def play_next_in_playlist(self) -> None:
        while self.playlist:
            video = self.playlist.pop(0)
            script = find_script(video)
            if video.is_file() and script is not None and script.is_file():
                self.video_path.set(str(video))
                self.script_path.set(f"✓  {script}")
                self.script_label.configure(foreground=COLORS["success"])
                remaining = len(self.playlist) + 1
                self.set_status(
                    (f"Automatic playback: {video.name} — {remaining} remaining" if LANGUAGE == "en" else f"Lecture automatique : {video.name} — {remaining} restante(s)"),
                    "success",
                )
                self.launch(video, script)
                return

        self.playlist_active = False
        self.delete_after_natural_end = False
        self.current_video = None
        self.current_script = None
        self.set_status(self.t("Toutes les vidéos du dossier ont été traitées."), "success")
        messagebox.showinfo(self.t("Terminé"), self.t("La lecture du dossier est terminée."))

    def delete_completed_files(self, video: Path, script: Path | None) -> list[str]:
        """Supprime uniquement les fichiers correspondant exactement à la vidéo terminée."""
        deleted: list[str] = []
        errors: list[str] = []

        targets = [video, *script_candidates_for_deletion(video, script)]
        seen: set[Path] = set()
        for target in targets:
            try:
                resolved = target.resolve()
            except OSError:
                resolved = target.absolute()
            if resolved in seen:
                continue
            seen.add(resolved)

            if not target.is_file():
                continue
            try:
                target.unlink()
                deleted.append(str(target))
            except OSError as exc:
                errors.append(f"{target}: {exc}")

        if errors:
            messagebox.showwarning(
                self.t("Suppression partielle"),
                (("Some files could not be deleted:\n\n" if LANGUAGE == "en" else "Certains fichiers n’ont pas pu être supprimés :\n\n") + "\n".join(errors)),
            )
        return deleted

    def check_process(self) -> None:
        if self.process is None:
            return

        code = self.process.poll()
        if code is None:
            self.after(100, self.check_process)
            return

        finished_video = self.current_video
        finished_script = self.current_script
        self.process = None

        if self.manual_next_requested:
            self.manual_next_requested = False
            self.current_video = None
            self.current_script = None

            if self.playlist_active and self.playlist:
                self.after(50, self.play_next_in_playlist)
            else:
                self.playlist_active = False
                self.set_status(self.t("Aucune vidéo suivante disponible."), "warning")
            return

        # Le moteur retourne 20 uniquement lorsque MPV a atteint la vraie fin.
        if code == 20:
            deleted_count = 0

            if (
                self.playlist_active
                and self.delete_after_end_var.get()
                and not self.stop_requested
                and finished_video is not None
            ):
                deleted = self.delete_completed_files(finished_video, finished_script)
                deleted_count = len(deleted)

            if (
                self.playlist_active
                and self.play_next_var.get()
                and not self.stop_requested
            ):
                if deleted_count:
                    self.set_status(
                        ((f"Natural end: {finished_video.name if finished_video else 'video'} deleted ({deleted_count} file(s)). Moving to the next…" if LANGUAGE == "en"
                          else f"Fin naturelle : {finished_video.name if finished_video else 'vidéo'} supprimée ({deleted_count} fichier(s)). Passage à la suivante…")),
                        "success",
                    )
                else:
                    self.set_status(
                        ("Natural end. Moving to the next video…" if LANGUAGE == "en" else "Fin naturelle. Passage à la vidéo suivante…"),
                        "success",
                    )
                self.after(50, self.play_next_in_playlist)
            else:
                self.playlist_active = False
                self.playlist.clear()
                if deleted_count:
                    self.set_status(
                        ((f"Playback finished naturally. {deleted_count} file(s) deleted." if LANGUAGE == "en"
                          else f"Lecture terminée naturellement. {deleted_count} fichier(s) supprimé(s).")),
                        "success",
                    )
                else:
                    self.set_status(self.t("Lecture terminée naturellement."), "neutral")
        elif code == 0:
            self.set_status(
                self.t("Lecture fermée avant la fin : aucun fichier supprimé."),
                "warning",
            )
            if self.playlist_active:
                self.playlist_active = False
                self.playlist.clear()
        else:
            self.set_status(
                (f"Player stopped with code {code}. No files deleted." if LANGUAGE == "en" else f"Le lecteur s'est arrêté avec le code {code}. Aucun fichier supprimé."),
                "danger",
            )
            if self.playlist_active:
                self.playlist_active = False
                self.playlist.clear()

        self.current_video = None
        self.current_script = None

    def stop(self) -> None:
        self.stop_requested = True
        self.manual_next_requested = False
        self.playlist_active = False
        self.delete_after_natural_end = False
        self.playlist.clear()
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            self.set_status(self.t("Arrêt demandé… aucun fichier ne sera supprimé."), "warning")
        self.process = None

    def load_config(self) -> None:
        try:
            data = json.loads(CONFIG.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        self.max_power.set(float(data.get("max_power", 0.80)))
        self.zero_hold.set(int(data.get("zero_hold", 150)))
        self.smoothing.set(float(data.get("smoothing", 0.20)))
        self.min_power.set(float(data.get("min_power", 0.08)))
        self.amplification.set(float(data.get("amplification", 0.0)))
        self.fullscreen.set(bool(data.get("fullscreen", True)))
        self.pump_enabled.set(bool(data.get("pump_enabled", False)))
        self.pump_seconds.set(float(data.get("pump_seconds", 0.12)))
        self.release_seconds.set(float(data.get("release_seconds", 0.12)))
        self.vibration_pattern.set(str(data.get("vibration_pattern", "progressif3")))
        self.delete_after_end_var.set(
            bool(data.get("delete_after_end", False))
        )
        self.play_next_var.set(
            bool(data.get("play_next", True))
        )
        self.language = str(data.get("language", "fr"))

    def save_config(self) -> None:
        CONFIG.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "max_power": self.max_power.get(),
            "zero_hold": int(self.zero_hold.get()),
            "smoothing": self.smoothing.get(),
            "min_power": self.min_power.get(),
            "amplification": self.amplification.get(),
            "fullscreen": self.fullscreen.get(),
            "pump_enabled": self.pump_enabled.get(),
            "pump_seconds": self.pump_seconds.get(),
            "release_seconds": self.release_seconds.get(),
            "vibration_pattern": self.vibration_pattern.get(),
            "delete_after_end": self.delete_after_end_var.get(),
            "play_next": self.play_next_var.get(),
            "language": self.language,
        }
        CONFIG.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def on_close(self) -> None:
        self.save_config()
        self.stop()
        try:
            self.progress_file.unlink(missing_ok=True)
        except OSError:
            pass
        self.destroy()


def main() -> int:
    app = VibrationPlayerGUI()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
