#!/usr/bin/env python


class Report(object):
    def __init__(self, filename, *args, **kwargs):
        self.data = open(filename, 'r')


class MOM4Report(Report):

    def __init__(self, filename, args, kwargs):
        super(MOM4Report, self).__init__(filename, args, kwargs)

    def apply_checks(self):
        for line in self.data:
            self.check_bctss()

    def check_bctss(self):
        ''' Checks Baroclinic time step stability.

        From fms.out:

 Baroclinic time step stability most nearly violated at U-cell (i,j) = ( 345, 454), (lon,lat) = (******, 67.92).
         The number of kmu-levels  at this point is      8
         The dxu grid distance (m) at this point is 0.210724E+05
         The dyu grid distance (m) at this point is 0.122441E+05
         Due to a specified maximum baroclinic gravity wave speed of  2.00 m/s.
         "dtuv" must be less than  5293. sec. "dtuv" =  1200. sec.
        '''
        pass

    def check_bts(self):
        ''' Checks Barotropic stability.

        From fms.out:

 Barotropic stability most nearly violated at U-cell (i,j) = ( 168, 460), (lon,lat) = (******, 88.67).
         The number of kmu-levels at this point is     57
         The dxu grid spacing (m) at this point is 0.123579E+05
         The dyu grid spacing (m) at this point is 0.554381E+05
         where the barotropic gravity wave speed is ~234.0 m/s.
         "dtbt" must be less than   56.000 sec.   dtbt =   12.000 sec.
        '''
        pass

    def check_vcfl(self):
        ''' Checks Vertical CFL.

        From fms.out:

                                                            Vertical CFL summary II:

 Locations (if any) where vertical Courant number exceeds 10.00

 w_bt (-0.460E-03 m/s) is   54.76 % of CFL ( 0.839E-03 m/s) at (i,j,k) = ( 478, 403, 30), (lon,lat,dpt) = (     -41.250,      61.250,   201.108 m)
 where grid is (m) (dxte,dytn,dzwu) = (   0.267E+05,   0.556E+05,     1.007
 The number of cells in the column are kmt =     42
 The grid dimensions (dst,rho_dzt) =    -1.515206582336E+05,     1.544443687778E+04
        '''
        pass

    def check_hcfl(self):
        ''' Checks Horizontal CFL.

        From fms.out:

                                                            Horizontal CFL summary II:

 Locations (if any) where horizontal Courant number exceeds 10.00

 v (  1.08     m/s) is    4.67 % of CFL (  23.2     m/s) at (i,j,k) = ( 641, 209,  1), (lon,lat,thk) = (      40.500,      -5.250,     2.532 m)
 u (  1.59     m/s) is    3.43 % of CFL (  46.3     m/s) at (i,j,k) = ( 275, 232, 16), (lon,lat,thk) = (    -142.500,       0.500,    78.372 m)
 where grid is (m) (dxu,dyu,dzu) = (   0.554E+05,   0.278E+05,     5.064
 where grid is (m) (dxu,dyu,dzu) = (   0.556E+05,   0.278E+05,     5.051
        '''
        pass

    def check_bvv(self):
        ''' Checks Bottom Vertical Velocity.

        from fms.out:

 Maximum T-cell bottom velocity ( 2.436E-16 m/s){error}  at (i,j,k) = ( 163, 458,  55), (lon,lat,dpt) = (-247.47,  87.69,  3750.m)
 Maximum U-cell bottom velocity ( 8.418E-04 m/s){slope}  at (i,j,k) = (   1,  50,  50), (lon,lat,dpt) = (-279.50, -65.00,  2303.m)
        '''
        pass

    def check_ce(self):
        ''' Checks Continuity error.

        from fms.out:

 Maximum T-cell Continuity Error (-2.145E-19 m/s) is at (i,j,k) = ( 353,234, 48),  (lon,lat,dpt) = (  -103.75,     0.88,  1825.09 m)


 Maximum U-cell Continuity Error ( 2.145E-19 m/s) is at (i,j,k) = ( 354,234, 47),  (lon,lat,dpt) = (  -103.00,     1.00,  1611.09 m)
        '''
        pass
