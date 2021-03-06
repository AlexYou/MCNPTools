"""
SPESpectra

Spe spectra file

"""

class SPESpectra(object):
    """
    SPE Spectra file. 
    
    Representation of the SPE spectra file according the the MAESTRO manuals.
    """

    def parseField(self,fieldname,token):
        """ parses text for a given field name
            fieldname - the name of the field
            token     - paresed fieldname token    
        """
        content = token.splitlines()
        field = ''
        for c in content:
            if not c.lower().startswith(fieldname):
                field += c
        return field
        
    def __init__(self,filename):
        """ File format from ORTEC Manual 
        
        Attributes:
          filename    - filename of the spectra
          spec_id     - one line of text describing the data
          spec_rem    - any number of lines containing remarks about data
          date_mea    - measurement date in the form mm/dd/yyyy hh:mm:ss
          meas_tim    - live time and realtime of the spectrum 
          data        - channel number and corresponding data
          roi         - regions of intrest
          energ_fit   - energy calibration (a+b*chn)
          mca_cal     - energy calibration along with mca calibration
          shape_cal   - FWHM calibration factors
        """
        self.filename = filename
        with open(filename,'r') as f:
            data = f.read()
        tokens = data.split('$')
        for t in tokens:
            # Ignorning strings that don't contain characters
            if not t.strip():
                continue
            # Getting the corresponding field
            field = t.splitlines()[0].lower()
            
            # Filling the fields
            if field.startswith('spec_id'):
                self.spec_id = self.parseField('spec_id',t)
            elif field.startswith('spec_rem'):
                self.spec_rem = self.parseField('spec_rem',t)
            elif field.startswith('date_mea'):
                date = self.parseField('date_mea',t)
                self.date_mea = date
            elif field.startswith('meas_tim'):
                data = self.parseField('meas_tim',t)
                times = data.split()
                self.meas_tim = {'Live time':float(times[0]),'Real time':float(times[1])}
            elif field.startswith('data'):
                lines = t.splitlines()
                channels = [int(i) for i in lines[1].split()]
                channels = range(channels[0],channels[1])
                data = [int(i) for i in lines[2:-1]]
                self.data = {'channels':channels,'data':data}
            elif field.startswith('roi'):
                lines = t.splitlines()
                self.roi = list()
                for line in lines[2:len(lines)]:
                    self.roi.append([int(i) for i in line.split()])
            elif field.startswith('ener_fit'):
                lines = t.splitlines()
                self.ener_fit = list()
                for line in lines[1:len(lines)]:
                    self.ener_fit.append([float(i) for i in line.split()])
            elif field.startswith('mca_cal'):
                lines = t.splitlines()
                self.mca_cal = list()
                for line in lines[2:len(lines)]:
                    self.mca_cal.append([float(i) for i in line.split()])
            elif field.startswith('shape_cal'):
                lines = t.splitlines()
                self.shape_cal = list()
                for line in lines[2:len(lines)]:
                    self.shape_cal.append([float(i) for i in line.split()])
            elif field.startswith('presets'):
                pass
            else:   
                print 'Unkown field: '+field
    def countRate(self,roi=None):
        """
        countRate(self,roi)
        
                Returns the count rate in a given region of intrest.  If a
                region of intrest is not suplied (as a 2D array) than the count
                rate of the entire spectrum is returned.
        """
        import math
        if roi is None:
            roi = [0,len(self.data['channels'])]
        cr = sum(self.data['data'][roi[0]:roi[1]+1])
        cr = [cr/self.meas_tim['Live time'], math.sqrt(cr)/self.meas_tim['Live time']]
        return  cr
        
    def roiAnalysis(self,roi=None):
        """
        Calculates the count rate in each of the ROI's
        
        roi - an 2D array of Region of Intrest (ROI's). If the ROI's are not
                provided, than any ROI's in the spectra are used.  If none are
                there, than nothing is returned
        """
        import math
        # Allocating data and reassinging the ROI if necessary
        data = list()
        if roi is None:
            roi = self.roi
            
        # Calculating the ROI
        s = 'ROI Analysis:'
        for r in roi:
            l = r[0]
            h = r[1]
            B = (sum(self.data['data'][l:l+3])+sum(self.data['data'][h-2:h+1]))/6.0*(h-l+1)
            Ag = float(sum(self.data['data'][l:h+1]))
            Aag = float(sum(self.data['data'][l+3:h-3+1]))
            An = Aag - float(B*(h-l-5)/float(h-l+1))
            sigmaAn = math.sqrt(Aag+B*((h-l-5)/6.0)*(h-l-5.0)/(h-l+1.0))
            s += '\n\tROI: {} to {}'.format(r[0],r[1])
            s += '\n\tBackground: {0:12.2f}\n\tGross:{1:17.2f}\n\tAdjusted Gross:{2:8.2f}\n\tNet: {3:20.2f}'.format(B,Ag,Aag,An)
            s += '\n\tNet Error: {0:13.2f}\n'.format(sigmaAn)
            data.append([An,sigmaAn])
        return data
        
    def plot(self):
        """
        Plots the data using pyplot
        """
        import matplotlib.pyplot as plt
        import numpy as np
        plt.plot(self.data['channels'], np.array(self.data['data'])/self.meas_tim['Live time'])
        plt.title(self.filename)
        plt.xlabel('Channel Number')
        plt.ylabel('Count Rate (cps)')
        plt.show()            
                
                
    def __str__(self):
        """
        String representation
        """
        attrs =  vars(self)
        headers = ['filename','spec_id','spec_rem','date_mea','meas_tim']
        data = ['roi','ener_fit','mca_cal','shape_cal']
        # need to print data
        s = ''.join("%s: %s\n" % (key,str(attrs[key])) for key in headers)
        s += 'channels: '+str(len(self.data['channels']))+'\n'
        s += ''.join("%s: %s\n" % (key,str(attrs[key])) for key in data)
        return s
    
    def __repr__(self):
        """
        Representation of the object
        """
        attrs =  vars(self)
        return ''.join("%s: %s\n" % item for item in attrs.items())
