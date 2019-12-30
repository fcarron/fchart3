#    fchart draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005-202 fchart authors0
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
from math import pi
from numpy import *
import string

from .label_potential import *
from .astrocalc import *
from .constellation import *
from .widget_mag_scale import *
from .widget_map_scale import *
from .mirroring_graphics import *
import fchart3.deepsky_object as deepsky


NL = {
    'h':'u',
    'm':'m',
    's':'s',
    'G':'Sterrenstelsel',
    'OCL':'Open sterrenhoop',
    'GCL':'Bolhoop',
    'AST':'Groepje sterren',
    'PN': 'Planetaire nevel',
    'N': 'Diffuse emissienevel',
    'SNR':'Supernovarest',
    'PG':'Deel van sterrenstelsel'
    }


EN = {
    'h':'h',
    'm':'m',
    's':'s',
    'G':'Galaxy',
    'OCL':'Open cluster',
    'GCL':'Globular cluster',
    'AST':'Asterism',
    'PN': 'Planetary nebula',
    'N': 'Diffuse nebula',
    'SNR':'Supernova remnant',
    'PG':'Part of external galaxy'
    }

STAR_LABELS = {
    "alp":"α",
    "bet":"β",
    "gam":"γ",
    "del":"δ",
    "eps":"ε",
    "zet":"ζ",
    "eta":"η",
    "the":"θ",
    "iot":"ι",
    "kap":"κ",
    "lam":"λ",
    "mu":"μ",
    "nu":"ν",
    "xi":"ξ",
    "omi":"ο",
    "pi":"π",
    "rho":"ρ",
    "sig":"σ/ς",
    "tau":"τ",
    "ups":"υ",
    "phi":"φ",
    "chi":"χ",
    "psi":"ψ",
    "ome":"ω"
    };

STARS_IN_SCALE = 7
LEGEND_MARGIN = 0.47
BASE_SCALE=0.98
DEFAULT_FONT_SIZE=2.6

DEFAULT_STAR_BORDER_LINEWIDTH = 0.06
DEFAULT_OPEN_CLUSTER_LINEWIDTH = 0.3
DEFAULT_DSO_LINEWIDTH = 0.2
DEFAULT_LEGEND_LINEWIDTH = 0.2
DEFAULT_CONSTELLATION_LINEWIDTH = 0.5

#====================>>>  SkymapEngine  <<<====================

class SkymapEngine:

    def __init__(self, graphics, language=EN, ra=0.0, dec=0.0, fieldradius=-1.0, lm_stars=13.8, caption=''):
        """
        Width is width of the map including the legend in mm.
        """
        self.graphics = graphics

        self.caption = ''
        self.language = language
        self.drawingwidth = self.graphics.gi_width
        self.min_radius   = 1.0 # of deepsky symbols (mm)

        self.lm_stars     = lm_stars
        self.deepsky_label_limit = 15 # deepsky lm for labels

        self.set_caption(caption)
        self.set_field(ra,dec,fieldradius)
        self.show_dso_legend = False

        self.star_border_linewidth = DEFAULT_STAR_BORDER_LINEWIDTH
        self.open_cluster_linewidth = DEFAULT_OPEN_CLUSTER_LINEWIDTH
        self.dso_linewidth = DEFAULT_DSO_LINEWIDTH
        self.legend_linewidth = DEFAULT_LEGEND_LINEWIDTH
        self.constellation_linewidth = DEFAULT_CONSTELLATION_LINEWIDTH

        self.invert_colors = False

        self.mirror_x = False
        self.mirror_y = False


    def set_field(self, ra, dec, fieldradius):
        """
        Provide the RA, DEC, and radius of the map in radians. This method
        sets a new drawingscale and legend_fontscale
        """
        self.fieldcentre         = (ra,dec)
        self.fieldradius         = fieldradius
        self.drawingscale        = BASE_SCALE * self.drawingwidth/2.0/sin(fieldradius)
        self.legend_fontscale    = self.drawingwidth/100.0

        self.set_caption(self.caption)

    def get_field_radius_mm(self):
        return self.drawingscale * sin(self.fieldradius)

    def set_language(language):
        """
        Set the language of the legend.
        """
        self.language = language


    def set_caption(self, caption):
        self.caption = caption
        if caption == '':
            self.graphics.set_dimensions(self.drawingwidth, self.drawingwidth)
        else:
            self.graphics.set_dimensions(self.drawingwidth,self.drawingwidth + self.legend_fontscale*self.graphics.gi_fontsize*2.0)


    def set_show_dso_legend(self, show_dso_legend):
        self.show_dso_legend =show_dso_legend


    def set_invert_colors(self, invert_colors):
        self.invert_colors = invert_colors


    def set_mirror_x(self, mirror_x):
        self.mirror_x = mirror_x


    def set_mirror_y(self, mirror_y):
        self.mirror_y = mirror_y


    def set_star_border_linewidth(self, star_border_linewidth):
        self.star_border_linewidth = star_border_linewidth


    def set_open_cluster_linewidth(self, open_cluster_linewidth):
        self.open_cluster_linewidth = open_cluster_linewidth

    def set_constellation_linewidth(self, constellation_linewidth):
        self.constellation_linewidth = constellation_linewidth

    def set_dso_linewidth(self, dso_linewidth):
        self.dso_linewidth = dso_linewidth


    def set_legend_linewidth(self, legend_linewidth):
        self.legend_linewidth = legend_linewidth


    def draw_caption(self):
        if self.caption != '':
            old_size = self.graphics.gi_fontsize
            font_size = self.get_legend_font_size()
            self.graphics.set_font(self.graphics.gi_font, 2.0*font_size)
            self.graphics.text_centred(0,self.drawingwidth/2.0*BASE_SCALE + font_size, self.caption)
            self.graphics.set_font(self.graphics.gi_font, old_size)


    def draw_field_border(self):
        """
        Draw a circle representing bthe edge of the field of view.
        """
        self.graphics.set_linewidth(self.legend_linewidth)
        r = self.get_field_radius_mm()
        self.graphics.line(-r, -r, -r, r)
        self.graphics.line(-r, r, r, r)
        self.graphics.line(r, r, r, -r)
        self.graphics.line(r, -r, -r, -r)


    def draw_coordinates(self, x, y, ra, dec):
        """
        x,y are coordinates of the lower left corner of the textbox
        """
        rah = int(ra*12/pi)
        ram = int((ra*12/pi -rah)*60)
        ras = int(((ra*12/pi -rah)*60 - ram)*60+0.5)
        if ras == 60:
            ram +=1
            ras = 0
        if ram == 60:
            rah += 1
            ram = 0
        if rah == 24:
            rah = 0

        decsign = '+'
        if dec < 0.0:
            decsign = '-'
        decd= int(abs(dec)*180/pi)
        decm = int((abs(dec)*180/pi-decd)*60)
        decs = int( ((abs(dec)*180/pi-decd)*60 -decm)*60 + 0.5)

        if decs == 60:
            decm += 1
            decs = 0
        if decm == 60:
            decm = 0

        text = str(rah).rjust(2) + self.language['h'] + str(ram) + self.language['m'] + str(ras) + self.language['s'] + \
             ' ' + decsign + str(decd) + '°' + str(decm) + '\'' + str(decs) + '"'

        self.graphics.text_left(x, y, text)


    def get_legend_font_size(self):
        return DEFAULT_FONT_SIZE*self.legend_fontscale


    def draw_legend(self, w_mag_scale, w_map_scale):
        # Set the fontsize for the entire legend
        fontsize = self.get_legend_font_size()
        self.graphics.set_font(self.graphics.gi_font, fontsize=fontsize)

        r = self.get_field_radius_mm()

        w_mag_scale.draw(self.graphics, -r, -r)
        w_map_scale.draw(self.graphics, r,-r)

        # Draw border of field-of-view
        self.draw_field_border()

        # Draw orientation indication
        dl = 0.02*self.drawingwidth
        x = -self.get_field_radius_mm() + dl + 0.2*fontsize
        y =  self.get_field_radius_mm() - dl - fontsize*1.3
        y_axis_caption = 'S' if self.mirror_y else 'N'
        self.graphics.text_centred(x, y + dl + 0.65*fontsize, y_axis_caption)
        x_axis_caption = 'E' if self.mirror_x else 'W'
        self.graphics.text_right(x+dl+fontsize/6.0, y-fontsize/3.0, x_axis_caption)

        self.graphics.line(x-dl, y, x+dl,y)
        self.graphics.line(x,y-dl, x,y+dl)

        # Draw coordinates of fieldcentre
        self.draw_coordinates(x=r-fontsize/2,
                              y=r-fontsize,
                              ra=self.fieldcentre[0],
                              dec=self.fieldcentre[1])

    def draw_dso_legend(self):
        fh = self.graphics.gi_fontsize
        # Draw list of symbols
        legendx  = 0.48*self.drawingwidth
        legendy  = 0.49*self.drawingwidth
        legendinc= fh

        r = fh/3.0
        text_offset = -2.5*r

        toplabels=[('OCL', len(self.language['OCL'])),
                   ('AST', len(self.language['AST'])),
                   ('G', len(self.language['G'])),
                   ('GCL', len(self.language['GCL']))]
        bottomlabels=[('SNR', len(self.language['SNR'])),
                      ('N',len(self.language['N'])),
                      ('PN', len(self.language['PN'])),
                      ('PG',len(self.language['PG']))]

        def labsort(x,y):
            r = 0
            if x[1] < y[1]:
                r = -1
            if x[1] > y[1]:
                r = 1
            return r

        toplabels.sort(key = deepsky.cmp_to_key(labsort))
        toplabels.reverse()
        tl = []
        for lab in toplabels:
            tl.append(lab[0])

        bottomlabels.sort(key = deepsky.cmp_to_key(labsort))
        bottomlabels.reverse()
        bl = []
        for lab in bottomlabels:
            bl.append(lab[0])

        self.open_cluster(legendx, legendy - (tl.index('OCL') + 1)*legendinc, r)
        self.graphics.text_left(legendx + text_offset, legendy - (tl.index('OCL') + 1)*legendinc - fh/3.0, self.language['OCL'])

        self.asterism(legendx, legendy - (tl.index('AST') + 1)*legendinc, r)
        self.graphics.text_left(legendx + text_offset, legendy - (tl.index('AST') + 1)*legendinc - fh/3.0, self.language['AST'])

        self.galaxy(legendx, legendy - (tl.index('G') + 1)*legendinc, r)
        self.graphics.text_left(legendx + text_offset, legendy - (tl.index('G') + 1)*legendinc - fh/3.0, self.language['G'])

        self.globular_cluster(legendx, legendy  - (tl.index('GCL') +1 )*legendinc, r)
        self.graphics.text_left(legendx + text_offset, legendy - (tl.index('GCL') + 1)*legendinc - fh/3.0, self.language['GCL'])

        legendy = LEGEND_MARGIN*self.drawingwidth

        self.supernova_remnant(legendx, -legendy + bl.index('SNR')*legendinc, r)
        self.graphics.text_left(legendx + text_offset, -legendy + bl.index('SNR')*legendinc - fh/3.0, self.language['SNR'])

        self.planetary_nebula(legendx, -legendy + bl.index('PN')*legendinc, r)
        self.graphics.text_left(legendx + text_offset, -legendy+bl.index('PN')*legendinc -  fh/3.0, self.language['PN'])

        self.diffuse_nebula(legendx, -legendy + bl.index('N')*legendinc, r)
        self.graphics.text_left(legendx + text_offset, -legendy + bl.index('N')*legendinc - fh/3.0, self.language['N'])

        self.unknown_object(legendx, -legendy + bl.index('PG')*legendinc, r)
        self.graphics.text_left(legendx + text_offset, -legendy + bl.index('PG')*legendinc - fh/3.0, self.language['PG'])


    def draw_deepsky_objects(self, deepsky_catalog):
        # Draw deep sky
        print('Drawing deepsky...')
        deepsky_list = deepsky_catalog.select_deepsky(self.fieldcentre, self.fieldradius).deepsky_list
        if len(deepsky_list) == 1:
            print('1 deepsky object in map.')
        else:
            print(str(len(deepsky_list))+' deepsky objects in map.')

        deepsky_list.sort(key = lambda x: x.mag)
        deepsky_list_mm = []
        for object in deepsky_list:
            l, m  =  radec_to_lm((object.ra, object.dec), self.fieldcentre)
            x, y   = -l*self.drawingscale, m*self.drawingscale
            rlong  = object.rlong*self.drawingscale
            if object.type == deepsky.GALCL:
                rlong = self.min_radius
            if rlong < self.min_radius:
                rlong = self.min_radius
            deepsky_list_mm.append((x, y, rlong))

        label_potential = LabelPotential(self.get_field_radius_mm(), deepsky_list_mm)

        print('Drawing objects...')
        for i in range(len(deepsky_list)):
            object = deepsky_list[i]

            x, y, rlong  = deepsky_list_mm[i]
            rlong  = object.rlong*self.drawingscale
            rshort = object.rshort*self.drawingscale
            posangle=object.position_angle+direction_ddec(\
                (object.ra, object.dec), self.fieldcentre)+0.5*pi

            if rlong <= self.min_radius:
                rshort *= self.min_radius/rlong
                rlong = self.min_radius

            if object.type == deepsky.GALCL:
                rlong /= 3.0

            label=''
            if object.messier > 0:
                label = 'M '+str(object.messier)
            elif object.cat == 'NGC':
                object.all_names.sort()
                label = '-'.join(object.all_names)
                if object.mag > self.deepsky_label_limit:
                    label = ''
            else :
                label = object.cat+' '+'-'.join(object.all_names)
                if object.mag > self.deepsky_label_limit:
                    label = ''

            label_length = self.graphics.text_width(label)
            labelpos = -1

            labelpos_list =[]
            if object.type == deepsky.G:
                labelpos_list = self.galaxy_labelpos(x, y, rlong, rshort, posangle, label_length)
            elif object.type == deepsky.N:
                labelpos_list = self.diffuse_nebula_labelpos(x, y, 2.0*rlong, 2.0*rshort, posangle, label_length)
            elif object.type in [deepsky.PN,deepsky.OC,deepsky.GC,deepsky.SNR]:
                labelpos_list = self.circular_object_labelpos(x, y, rlong, label_length)
            elif object.type == deepsky.STARS:
                labelpos_list = self.asterism_labelpos(x, y, rlong, label_length)
            else:
                labelpos_list = self.unknown_object_labelpos(x, y, rlong, label_length)

            pot = 1e+30
            for labelpos_index in range(len(labelpos_list)):
                [[x1,y1],[x2,y2],[x3,y3]] = labelpos_list[labelpos_index]
                pot1 = label_potential.compute_potential(x2,y2)
                #label_potential.compute_potential(x1,y1),
                #label_potential.compute_potential(x3,y3)])
                if pot1 < pot:
                    pot = pot1
                    labelpos = labelpos_index

            [xx, yy] = labelpos_list[labelpos][1]
            label_potential.add_position(xx, yy, label_length)

            if object.type == deepsky.G:
                self.galaxy(x, y, rlong, rshort, posangle, label, labelpos)
            elif object.type == deepsky.N:
                self.diffuse_nebula(x, y, 2.0*rlong, 2.0*rshort, posangle, label, labelpos)
            elif object.type == deepsky.PN:
                self.planetary_nebula(x, y, rlong, label, labelpos)
            elif object.type == deepsky.OC:
                self.open_cluster(x, y, rlong, label, labelpos)
            elif object.type == deepsky.GC:
                self.globular_cluster(x, y, rlong, label, labelpos)
            elif object.type == deepsky.STARS:
                self.asterism(x, y, rlong, label, labelpos)
            elif object.type == deepsky.SNR:
                self.supernova_remnant(x, y, rlong, label, labelpos)
            else:
                self.unknown_object(x, y, rlong, label, labelpos)


    def draw_extra_objects(self,extra_positions):
        # Draw extra objects
        print('Drawing extra objects...')
        for object in extra_positions:
            rax,decx,label,labelpos = object
            if angular_distance((rax,decx),self.fieldcentre) < self.fieldradius:
                l,m =  radec_to_lm((rax,decx), self.fieldcentre)
                x,y = -l*self.drawingscale, m*self.drawingscale
                self.unknown_object(x,y,self.min_radius,label,labelpos)


    def magnitude_to_radius(self, magnitude):
        #radius = 0.13*1.35**(int(self.lm_stars)-magnitude)
        radius = 0.15*1.33 ** (int(self.lm_stars) - magnitude)
        return radius

    def draw_stars(self, star_catalog):
        # Select and draw stars
        print('Drawing stars...')
        selection = star_catalog.select_stars(self.fieldcentre, self.fieldradius, self.lm_stars)
        print(str(selection.shape[0]) + ' stars in map.')
        print('Faintest star: ' + str(int(max(selection[:,2])*100.0 + 0.5)/100.0))

        l, m = radec_to_lm((selection[:,0], selection[:,1]), self.fieldcentre)
        x, y = -l, m

        mag       = selection[:,2]
        indices   = argsort(mag)
        magsorted = mag[indices]
        xsorted   = x[indices]*self.drawingscale
        ysorted   = y[indices]*self.drawingscale

        rsorted = self.magnitude_to_radius(magsorted)
        self.graphics.set_linewidth(self.star_border_linewidth)
        self.graphics.set_pen_gray(1.0)
        self.graphics.set_fill_gray(0.0)
        for i in range(len(xsorted)):
            if magsorted[i] <= 13.8:
                x = xsorted[i]
                y = ysorted[i]
                excluded = False
                if not excluded:
                    self.star(x, y, rsorted[i])
        self.graphics.set_pen_gray(0.0)


    def draw_constellations(self, constell_catalog):
        print('Drawing constellations...' + str(self.fieldcentre[0]))
        self.graphics.set_linewidth(self.constellation_linewidth)
        old_size = self.graphics.gi_fontsize
        self.graphics.set_font(self.graphics.gi_font, 1.3*old_size)
        printed = {}
        for star in constell_catalog.bright_stars:
            if (star.greek == '') or abs(star.ra-self.fieldcentre[0]) > pi/2.0:
                continue
            constell_printed = printed.get(star.constellation)
            if not constell_printed:
                constell_printed = set()
                printed[star.constellation] = constell_printed
            elif star.greek in constell_printed:
                continue

            constell_printed.add(star.greek)

            letter = STAR_LABELS.get(star.greek)
            if letter:
                l, m = radec_to_lm((star.ra, star.dec), self.fieldcentre)
                x, y = -l * self.drawingscale, m * self.drawingscale
                r = self.magnitude_to_radius(star.mag)
                self.draw_circular_object_label(x, y , r, letter)
            else:
                print("Unknown greek letter:" + star.greek)

        self.graphics.set_font(self.graphics.gi_font, old_size)

        self.graphics.set_pen_rgb((0.2, 0.7, 1.0))
        for constell in constell_catalog.constellations:
            for line in constell.lines:
                star1 = constell_catalog.bright_stars[line[0]-1]
                star2 = constell_catalog.bright_stars[line[1]-1]

                # just use hack for sin projection
                if abs(star1.ra-self.fieldcentre[0]) > pi/2.0 or abs(star2.ra-self.fieldcentre[0]) > pi/2.0:
                    continue
                l1, m1 = radec_to_lm((star1.ra, star1.dec), self.fieldcentre)
                l2, m2 = radec_to_lm((star2.ra, star2.dec), self.fieldcentre)
                x1, y1 = -l1 * self.drawingscale, m1 * self.drawingscale
                x2, y2 = -l2 * self.drawingscale, m2 * self.drawingscale
                self.mirroring_graphics.line(x1, y1, x2, y2)
        self.graphics.set_pen_gray(0.0)


    def make_map(self, star_catalog=None, deepsky_catalog=None, constell_catalog=None, extra_positions=[]):
        if self.mirror_x or self.mirror_y:
            self.mirroring_graphics = MirroringGraphics(self.graphics, self.mirror_x, self.mirror_y)
        else:
            self.mirroring_graphics = self.graphics
        self.graphics.set_invert_colors(self.invert_colors)
        self.graphics.new()
        self.graphics.set_pen_gray(0.0)
        self.graphics.set_fill_gray(0.0)
        self.graphics.set_font(fontsize=DEFAULT_FONT_SIZE)
        self.graphics.set_linewidth(self.legend_linewidth)

        r = self.get_field_radius_mm()

        w_mag_scale = WidgetMagnitudeScale(self,
                                          field_radius_mm=r,
                                          legend_fontsize=self.get_legend_font_size(),
                                          stars_in_scale=STARS_IN_SCALE,
                                          lm_stars=self.lm_stars,
                                          star_border_linewidth=self.star_border_linewidth,
                                          legend_linewidth=self.legend_linewidth)

        w_map_scale = WidgetMapScale(drawingwidth=self.drawingwidth,
                                    drawingscale=self.drawingscale,
                                    maxlength=self.drawingwidth/3.0,
                                    legend_fontsize=self.get_legend_font_size(),
                                    legend_linewidth=self.legend_linewidth)

        w_mags_width, w_mags_heigth = w_mag_scale.get_size()
        w_maps_width, w_maps_height = w_map_scale.get_size()

        self.graphics.clip_path([(r,r),
                                 (r,-r+w_maps_height),
                                 (r-w_maps_width, -r+w_maps_height),
                                 (r-w_maps_width, -r),
                                 (-r + w_mags_width, -r),
                                 (-r + w_mags_width, -r + w_mags_heigth),
                                 (-r, -r + w_mags_heigth),
                                 (-r,r),
                                 ])

        if constell_catalog != None:
            self.draw_constellations(constell_catalog)
        if deepsky_catalog != None:
            self.draw_deepsky_objects(deepsky_catalog)
        if extra_positions != []:
            self.draw_extra_objects(extra_positions)
        if star_catalog != None:
            self.draw_stars(star_catalog)

        self.graphics.reset_clip()

        print('Drawing legend')
        self.draw_caption()

        self.draw_legend(w_mag_scale, w_map_scale)
        print('Drawing dso legend')
        if self.show_dso_legend:
            self.draw_dso_legend()

        self.graphics.finish()


    def star(self, x, y, radius, mirroring=True):
        """
        Filled circle with boundary. Set fill colour and boundary
        colour in advance using set_pen_gray and set_fill_gray
        """
        xx = int(x*100.0 + 0.5)/100.0
        yy = int(y*100.0 + 0.5)/100.0
        r = int((radius + self.graphics.gi_linewidth/2.0)*100.0 + 0.5)/100.0
        if mirroring:
            self.mirroring_graphics.circle(xx, yy, r,'PF')
        else:
            self.graphics.circle(xx, yy, r,'PF')


    def open_cluster(self, x, y, radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        self.graphics.save()

        self.graphics.set_linewidth(self.open_cluster_linewidth)
        self.graphics.set_dashed_line(0.6,0.4)
        self.mirroring_graphics.circle(x,y,r)

        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()


    def asterism(self,x,y,radius=-1, label='', labelpos=-1):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        w2=2**0.5
        d = r/2.0*w2

        self.graphics.save()

        self.graphics.set_linewidth(self.open_cluster_linewidth)
        self.graphics.set_dashed_line(0.6,0.4)
        diff = self.graphics.gi_linewidth/2.0/w2

        self.mirroring_graphics.line(x-diff, y+d+diff, x+d+diff,y-diff)
        self.mirroring_graphics.line(x+d, y, x,y-d)
        self.mirroring_graphics.line(x+diff, y-d-diff, x-d-diff,y+diff)
        self.mirroring_graphics.line(x-d, y, x,y+d)

        fh =  self.graphics.gi_fontsize
        if label != '':
            if labelpos == 0 or labelpos == -1:
                self.mirroring_graphics.text_centred(x, y-d-2*fh/3.0, label)
            elif labelpos == 1:
                self.mirroring_graphics.text_centred(x, y+d+fh/3.0, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_left(x-d-fh/6.0, y-fh/3.0, label)
            elif labelpos == 3:
                self.mirroring_graphics.text_right(x+d+fh/6.0, y-fh/3.0, label)
        self.graphics.restore()


    def asterism_labelpos(self,x,y,radius=-1,label_length=0.0):
        """
        x,y,radius, label_length in mm
        returns [[start, centre, end],()]
        """
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        w2=2**0.5
        d = r/2.0*w2
        fh =  self.graphics.gi_fontsize
        label_pos_list = []
        yy = y-d-2*fh/3.0
        label_pos_list.append([[x-label_length/2.0,yy],[x,yy],[x+label_length,yy]])
        yy = y+d+2*fh/3.0
        label_pos_list.append([[x-label_length/2.0,yy],[x,yy],[x+label_length,yy]])
        xx = x-d-fh/6.0
        yy = y
        label_pos_list.append([[xx-label_length,yy],[xx-label_length/2.0,yy],[xx,yy]])
        xx = x+d+fh/6.0
        yy = y
        label_pos_list.append([[xx,yy],[xx+label_length/2.0,yy],[xx+label_length,yy]])
        return label_pos_list


    def galaxy(self, x, y, rlong=-1, rshort=-1, posangle=0.0, label='', labelpos=-1):
        """
        If rlong != -1 and rshort == -1 =>   rshort <- rlong
        if rlong < 0.0 => standard galaxy
        labelpos can be 0,1,2,3
        """
        rl = rlong
        rs = rshort
        if rlong <= 0.0:
            rl = self.drawingwidth/40.0
            rs = rl/2.0
        if rlong > 0.0 and rshort < 0.0:
            rl = rlong
            rs = rlong/2.0

        self.graphics.save()

        self.graphics.set_linewidth(self.dso_linewidth)
        p = posangle
        if posangle >= 0.5*pi:
            p += pi
        if posangle < -0.5*pi:
            p -= pi

        fh = self.graphics.gi_fontsize
        self.mirroring_graphics.ellipse(x,y,rl, rs, p)
        if label != '':
            self.graphics.save()
            self.mirroring_graphics.translate(x,y)
            self.mirroring_graphics.rotate(p)
            if labelpos == 0 or labelpos == -1:
                self.graphics.text_centred(0, -rshort-0.5*fh, label)
            elif labelpos == 1:
                self.graphics.text_centred(0, +rshort+0.5*fh, label)
            elif labelpos == 2:
                self.graphics.text_right(rlong+fh/6.0, -fh/3.0, label)
            elif labelpos == 3:
                self.graphics.text_left(-rlong-fh/6.0, -fh/3.0, label)
            self.graphics.restore()
        self.graphics.restore()


    def galaxy_labelpos(self,x,y,rlong=-1,rshort=-1,posangle=0.0,label_length=0.0):
        rl = rlong
        rs = rshort
        if rlong <= 0.0:
            rl = self.drawingwidth/40.0
            rs = rl/2.0
        if rlong > 0.0 and rshort < 0.0:
            rl = rlong
            rs = rlong/2.0

        p = posangle
        if posangle >= 0.5*pi:
            p += pi
        if posangle < -0.5*pi:
            p -= pi

        fh = self.graphics.gi_fontsize
        label_pos_list = []

        sp = sin(p)
        cp = cos(p)

        hl = label_length/2.0

        d = -rshort-0.5*fh
        xc = x + d*sp
        yc = y - d*cp
        xs = xc -hl*cp
        ys = yc -hl*sp
        xe = xc +hl*cp
        ye = yc +hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        xc = x - d*sp
        yc = y + d*cp
        xs = xc -hl*cp
        ys = yc -hl*sp
        xe = xc +hl*cp
        ye = yc +hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        d  = rlong+fh/6.0
        xs = x + d*cp
        ys = y + d*sp
        xc = xs + hl*cp
        yc = ys + hl*sp
        xe = xc + hl*cp
        ye = yc + hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        xe = x - d*cp
        ye = y - d*sp
        xc = xe - hl*cp
        yc = ye - hl*sp
        xs = xc - hl*cp
        ys = yc - hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        return label_pos_list


    def draw_circular_object_label(self, x, y, r, label='', labelpos=-1):
        fh = self.graphics.gi_fontsize
        if label != '':
            arg = 1.0-2*fh/(3.0*r)
            if arg < 1.0 and arg > -1.0:
                a = arccos(arg)
            else:
                a = 0.5*pi
            if labelpos == 0 or labelpos == -1:
                self.mirroring_graphics.text_right(x+sin(a)*r+fh/6.0, y-r, label)
            elif labelpos == 1:
                self.mirroring_graphics.text_left(x-sin(a)*r-fh/6.0, y-r, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_right(x+sin(a)*r+fh/6.0, y+r-2*fh/3.0, label)
            elif labelpos == 3:
                self.mirroring_graphics.text_left(x-sin(a)*r-fh/6.0, y+r-2*fh/3.0, label)


    def circular_object_labelpos(self, x, y, radius=-1.0, label_length=0.0):
        fh = self.graphics.gi_fontsize
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        arg = 1.0-2*fh/(3.0*r)
        if arg < 1.0 and arg > -1.0:
            a = arccos(arg)
        else:
            a = 0.5*pi

        label_pos_list = []
        xs = x+sin(a)*r+fh/6.0
        ys = y-r+fh/3.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        xs = x-sin(a)*r-fh/6.0 - label_length
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x+sin(a)*r+fh/6.0
        ys = y+r-fh/3.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x+sin(a)*r+fh/6.0
        ys = y+r-fh/3.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        return label_pos_list



    def globular_cluster(self, x,y,radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        self.graphics.save()

        self.graphics.set_linewidth(self.dso_linewidth)
        self.mirroring_graphics.circle(x,y,r)
        self.mirroring_graphics.line(x-r, y, x+r, y)
        self.mirroring_graphics.line(x, y-r, x, y+r)

        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()


    def diffuse_nebula(self, x, y, width=-1.0, height=-1.0, posangle=0.0, label='',labelpos=''):
        self.graphics.save()

        self.graphics.set_linewidth(self.dso_linewidth)
        d = 0.5*width
        if width < 0.0:
            d = self.drawingwidth/40.0
        d1 = d+self.graphics.gi_linewidth/2.0
        self.mirroring_graphics.line(x-d1, y+d, x+d1, y+d)
        self.mirroring_graphics.line(x+d, y+d, x+d, y-d)
        self.mirroring_graphics.line(x+d1, y-d, x-d1, y-d)
        self.mirroring_graphics.line(x-d, y-d, x-d, y+d)
        fh = self.graphics.gi_fontsize
        if label != '':
            if labelpos == 0 or labelpos == -1:
                self.mirroring_graphics.text_centred(x, y-d-fh/2.0, label)
            elif labelpos == 1:
                self.mirroring_graphics.text_centred(x, y+d+fh/2.0, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_left(x-d-fh/6.0, y-fh/3.0, label)
            elif labelpos == 3:
                self.mirroring_graphics.text_right(x+d+fh/6.0, y-fh/3.0, label)
        self.graphics.restore()


    def diffuse_nebula_labelpos(self,x,y,width=-1.0,height=-1.0, posangle=0.0,label_length=0.0):

        d = 0.5*width
        if width < 0.0:
            d = self.drawingwidth/40.0
        fh = self.graphics.gi_fontsize

        label_pos_list = []
        xs = x - label_length/2.0
        ys = y-d-fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        ys = y+d+fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x - d - fh/6.0 - label_length
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x + d + fh/6.0
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        return label_pos_list


    def planetary_nebula(self, x, y, radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/60.0
        self.graphics.save()

        self.graphics.set_linewidth(self.dso_linewidth)
        self.mirroring_graphics.circle(x,y,0.75*r)
        self.mirroring_graphics.line(x-0.75*r, y, x-1.5*r, y)
        self.mirroring_graphics.line(x+0.75*r, y, x+1.5*r, y)
        self.mirroring_graphics.line(x, y+0.75*r, x, y+1.5*r)
        self.mirroring_graphics.line(x, y-0.75*r, x, y-1.5*r)

        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()


    def supernova_remnant(self,x,y,radius=-1.0,label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        self.graphics.save()

        self.graphics.set_linewidth(self.dso_linewidth)
        self.mirroring_graphics.circle(x,y,r-self.graphics.gi_linewidth/2.0)
        #self.graphics.circle(x,y,r*0.85)
        #self.graphics.circle(x,y,r*0.7)
        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()

    def unknown_object(self,x,y,radius=-1.0,label='',labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0

        r/=2**0.5
        self.graphics.save()

        self.graphics.set_linewidth(self.dso_linewidth)
        self.mirroring_graphics.line(x-r, y+r, x+r, y-r)
        self.mirroring_graphics.line(x+r, y+r, x-r, y-r)
        fh = self.graphics.gi_fontsize
        if label != '':
            if labelpos == 0:
                self.mirroring_graphics.text_right(x+r+fh/6.0, y-fh/3.0, label)
            elif labelpos ==1:
                self.mirroring_graphics.text_left(x-r-fh/6.0, y-fh/3.0, label)
            elif labelpos == 2:
                self.mirroring_graphics.text_centred(x, y+ r + fh/2.0, label)
            else:
                self.mirroring_graphics.text_centred(x, y - r - fh/2.0, label)
        self.graphics.restore()


    def unknown_object_labelpos(self,x,y,radius=-1,label_length=0.0):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
        fh = self.graphics.gi_fontsize
        r/=2**0.5
        label_pos_list = []
        xs = x + r +fh/6.0
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x - r -fh/6.0 - label_length
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x -label_length/2.0
        ys = y + r +fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x -label_length/2.0
        ys = y - r -fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        return label_pos_list


if __name__ == '__main__':
    from . import cairo
    from . import star_catalog as sc

    stars = sc.StarCatalog('data/tyc2.bin')

    width = 200
    cairo = cairo.PDFDrawing('radec00.pdf',width, width)

    sm = SkymapEngine(cairo)
    sm.set_caption('Probeersel')
    sm.set_field(1.5,1, 0.05)
    sm.make_map(stars)
    cairo.close()

__all__ = ['EN', 'NL', 'SkymapEngine']
