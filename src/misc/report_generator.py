import os

import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class GenerateReport:

    def __init__(self, A, B, C, D, eigen_values, damping, sys):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.eigen_values = eigen_values
        self.damping = np.array(damping)
        self.sys = sys

    def write(self, file_name):
        path = os.getcwd()
        doc = SimpleDocTemplate(f"{path}/src/misc/report/{file_name}.pdf", pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Add matrices A and B in the same row
        elements.append(Paragraph("Matrix A and Matrix B", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Table([["Matrix A", "Matrix B"], [np.array2string(self.A), np.array2string(self.B)]], style=[
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(Spacer(1, 12))

        # Add matrices C and D in the same row
        elements.append(Paragraph("Matrix C and Matrix D", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Table([["Matrix C", "Matrix D"], [np.array2string(self.C), np.array2string(self.D)]], style=[
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(Spacer(1, 12))

        # Add eigen values
        elements.append(Paragraph("Eigen Values", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Table([[np.array2string(self.eigen_values)]], style=[
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(Spacer(1, 12))

        # Add damping table
        elements.append(Paragraph("Damping Table", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Table([[np.array2string(self.damping)]], style=[
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(Spacer(1, 12))

        doc.build(elements)

        print("Report generated successfully!")


