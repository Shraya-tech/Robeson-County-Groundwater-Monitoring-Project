import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
 
WELLS = [
    {"name":"Doc Henderson","line1":"Weekly r = 0.227  |  P = 0.0001","line2":"Black Creek CU: ABSENT","role":"breach","surf_elev":155.0,"total_depth":300,
     "layers":[("Surficial",155.0,133.0),("Black Creek CU",133.0,133.0),("Black Creek",133.0,-45.0),("Upper Cape Fear CU",-45.0,-134.0),("Upper Cape Fear",-134.0,-183.0),("Basement",-183.0,-300.0)]},
    {"name":"Bethel Hill","line1":"Weekly r = 0.157","line2":"Black Creek CU: 11 ft  (breach)","role":"breach","surf_elev":149.0,"total_depth":380,
     "layers":[("Surficial",149.0,149.0),("Black Creek CU",149.0,138.0),("Black Creek",138.0,-80.0),("Upper Cape Fear CU",-80.0,-167.0),("Upper Cape Fear",-167.0,-268.0),("Basement",-268.0,-380.0)]},
    {"name":"MW1","line1":"Weekly r = 0.075","line2":"Black Creek CU: 35 ft  (intact)","role":"control","surf_elev":131.0,"total_depth":400,
     "layers":[("Surficial",131.0,131.0),("Black Creek CU",131.0,96.0),("Black Creek",96.0,-152.0),("Upper Cape Fear CU",-152.0,-213.0),("Upper Cape Fear",-213.0,-322.0),("Basement",-322.0,-400.0)]},
    {"name":"Alamac","line1":"Weekly r = 0.184","line2":"Black Creek CU: 26 ft  (intact)","role":"control","surf_elev":107.0,"total_depth":400,
     "layers":[("Surficial",107.0,39.0),("Black Creek CU",39.0,13.0),("Black Creek",13.0,-247.0),("Upper Cape Fear CU",-247.0,-298.0),("Upper Cape Fear",-298.0,-369.0),("Basement",-369.0,-400.0)]},
    {"name":"Orum Water Tower","line1":"Weekly r = 0.075","line2":"Black Creek CU: 11 ft","role":"control","surf_elev":149.0,"total_depth":380,
     "layers":[("Surficial",149.0,149.0),("Black Creek CU",149.0,138.0),("Black Creek",138.0,-80.0),("Upper Cape Fear CU",-80.0,-167.0),("Upper Cape Fear",-167.0,-268.0),("Basement",-268.0,-380.0)]},
]
 
LAYER_COLORS = {
    "Surficial":"#C0DD97","Black Creek CU":"#C8C6BE","Black Creek":"#639922",
    "Upper Cape Fear CU":"#A09E97","Upper Cape Fear":"#1D9E75","Basement":"#5F5E5A",
}
LAYER_HATCH  = {"Black Creek CU":"///","Upper Cape Fear CU":"///","Basement":"xxx"}
LAYER_LABELS = {
    "Surficial":"Surficial Aq.","Black Creek CU":"Black Creek CU",
    "Black Creek":"Black Creek Aq.","Upper Cape Fear CU":"UCF Confining",
    "Upper Cape Fear":"Upper Cape Fear Aq.","Basement":"Basement Rock",
}
 
FS_LAYER_NAME  = 30
FS_THICKNESS   = 26
FS_ELEV_TICK   = 22
FS_SURFACE     = 24
FS_MSL         = 22
FS_YLABEL      = 28
FS_YTICK       = 22
FS_TITLE       = 34
FS_SUBTITLE    = 28
FS_ANNOTATION  = 28
FS_GROUP       = 36
FS_MAIN_TITLE  = 44
FS_SOURCE      = 24
FS_LEGEND      = 28
 
def draw_well(ax, well, show_ylabel=True):
    surf = well["surf_elev"]
    bot  = -well["total_depth"] - 50
    is_breach = well["role"] == "breach"
 
    for (lname, top, base) in well["layers"]:
        thickness = top - base
        if thickness <= 0:
            continue
        highlight = is_breach and lname == "Black Creek CU"
        ax.add_patch(plt.Rectangle(
            (0.05, base), 0.9, thickness,
            facecolor=LAYER_COLORS[lname],
            edgecolor="#B85042" if highlight else "#444444",
            linewidth=4.0 if highlight else 1.2,
            hatch=LAYER_HATCH.get(lname,""), alpha=0.93
        ))
        mid = (top + base) / 2
        if thickness >= 40:
            ax.text(0.50, mid, LAYER_LABELS[lname], ha='center', va='center',
                    fontsize=FS_LAYER_NAME, fontweight='bold', color='#1a1a1a',
                    path_effects=[pe.withStroke(linewidth=4, foreground='white')])
        if thickness >= 120:
            ax.text(0.50, mid - thickness*0.18, f"{thickness:.0f} ft",
                    ha='center', va='center', fontsize=FS_THICKNESS,
                    color='#333', style='italic',
                    path_effects=[pe.withStroke(linewidth=3, foreground='white')])
        ax.plot([0.95, 1.05], [top, top], color='#666', lw=1.5)
        ax.text(1.07, top, f"{top:+.0f} ft", va='center', ha='left',
                fontsize=FS_ELEV_TICK, color='#444')
 
    if is_breach:
        for (lname, top, base) in well["layers"]:
            if lname == "Black Creek CU":
                thickness = top - base
                ymid = (top+base)/2 if thickness>0 else surf-12
                label = "CU absent!" if thickness<=0 else f"CU only {thickness:.0f} ft!"
                ax.annotate(label, xy=(0.50, ymid), xytext=(0.50, ymid-90),
                    fontsize=FS_ANNOTATION, color='#B85042', fontweight='bold',
                    ha='center',
                    arrowprops=dict(arrowstyle='->', color='#B85042', lw=3.0))
 
    ax.axhline(surf, color='#4a7a20', lw=2.0, ls='--', alpha=0.75)
    ax.text(0.50, surf+18, f"Surface: {surf:.0f} ft", ha='center', va='bottom',
            fontsize=FS_SURFACE, color='#4a7a20', style='italic',
            path_effects=[pe.withStroke(linewidth=3, foreground='white')])
    ax.axhline(0, color='#3B8BD4', lw=1.2, ls=':', alpha=0.65)
    ax.text(0.07, 8, "MSL", va='bottom', ha='left', fontsize=FS_MSL, color='#3B8BD4')
    ax.set_xlim(0, 1.70); ax.set_ylim(bot, surf+110); ax.set_xticks([])
    if show_ylabel:
        ax.set_ylabel("Elevation (ft AMSL)", fontsize=FS_YLABEL, labelpad=8)
    ax.yaxis.set_tick_params(labelsize=FS_YTICK)
    for sp in ['top','right','bottom']: ax.spines[sp].set_visible(False)
 
def make_legend(fig, ncol=6):
    patches = [mpatches.Patch(facecolor=LAYER_COLORS[n], edgecolor='#444', lw=1.0,
        hatch=LAYER_HATCH.get(n,""), label=LAYER_LABELS[n]) for n in LAYER_COLORS]
    fig.legend(handles=patches, loc='lower center', ncol=ncol,
               fontsize=FS_LEGEND, framealpha=0.95, edgecolor='#ccc',
               bbox_to_anchor=(0.5, 0.002))
 
# FIGURE 1: All 5 wells
fig1, axes1 = plt.subplots(1, 5, figsize=(40, 22),
    gridspec_kw={'left':0.05,'right':0.96,'top':0.74,'bottom':0.12,'wspace':0.55})
fig1.patch.set_facecolor('white')
for i,(ax,well) in enumerate(zip(axes1,WELLS)):
    draw_well(ax, well, show_ylabel=(i==0))
    tc='#B85042' if well["role"]=="breach" else '#0A2E52'
    ax.set_title(f"{well['name']}\n{well['line1']}\n{well['line2']}",
        fontsize=FS_TITLE, fontweight='bold', color=tc, pad=22, linespacing=2.0)
fig1.add_artist(plt.Line2D([0.415,0.415],[0.11,0.76],transform=fig1.transFigure,color='#bbbbbb',lw=2.5,ls='--'))
fig1.text(0.21,0.93,"⚠  Breach / High Recharge",ha='center',fontsize=FS_GROUP,color='#B85042',fontweight='bold')
fig1.text(0.69,0.93,"●  Control Sites",ha='center',fontsize=FS_GROUP,color='#0A2E52',fontweight='bold')
fig1.text(0.5,0.985,"Hydrogeological Aquifer Layer Profiles — Robeson County RCGMP Wells",ha='center',fontsize=FS_MAIN_TITLE,fontweight='bold')
fig1.text(0.5,0.965,"Data: NCDEQ Division of Water Resources — ncwater.org  |  2018–2024",ha='center',fontsize=FS_SOURCE,color='#666')
make_legend(fig1, ncol=6)
plt.savefig('aquifer_all5_panel.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: aquifer_all5_panel.png")
 
# FIGURE 2: Breach comparison
compare_names = ["Doc Henderson","Bethel Hill","Alamac"]
cw = sorted([w for w in WELLS if w["name"] in compare_names], key=lambda w: compare_names.index(w["name"]))
fig2, axes2 = plt.subplots(1, 3, figsize=(28, 22),
    gridspec_kw={'left':0.08,'right':0.97,'top':0.74,'bottom':0.13,'wspace':0.60})
fig2.patch.set_facecolor('white')
for i,(ax,well) in enumerate(zip(axes2,cw)):
    draw_well(ax, well, show_ylabel=(i==0))
    tc='#B85042' if well["role"]=="breach" else '#0A2E52'
    ax.set_title(f"{well['name']}\n{well['line1']}\n{well['line2']}",
        fontsize=FS_TITLE+4, fontweight='bold', color=tc, pad=22, linespacing=2.0)
fig2.text(0.5,0.985,"The Breach Argument: Confining Unit Comparison",ha='center',fontsize=FS_MAIN_TITLE,fontweight='bold')
fig2.text(0.5,0.963,"Same permeable surface (~96% crops/trees) — very different geology beneath",ha='center',fontsize=FS_SOURCE+2,color='#555',style='italic')
make_legend(fig2, ncol=3)
plt.savefig('aquifer_breach_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: aquifer_breach_comparison.png")
print("\nDone!")
 