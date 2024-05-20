from bs4 import BeautifulSoup
import pandas as pd
from django.http import HttpResponse
from io import BytesIO

# Create your views here.
def download_excel(request):
    if request.method == 'POST':
        html_content = request.POST.get('html_content', '')
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')

        # Extract headers
        headers = [th.text.strip() for th in table.find_all('th')]

        # Extract rows
        rows = []
        for tr in table.find_all('tr')[1:]:
            cells = tr.find_all('td')
            row = [cell.text.strip() for cell in cells]
            rows.append(row)

        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)

        # Remove thousands separator and convert to float
        for col in df.columns:
            df[col] = df[col].str.replace(',', '').str.replace(' ALL', '')  # Remove commas and ' ALL'
            df[col] = pd.to_numeric(df[col], errors='ignore')  # Convert to numeric where possible

        # Create an Excel writer
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=report.xlsx'
        writer = pd.ExcelWriter(response, engine='xlsxwriter')

        # Write DataFrame to Excel
        df.to_excel(writer, index=False, sheet_name='Report')

        with BytesIO() as b:
            writer = pd.ExcelWriter(b, engine='openpyxl')
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            writer.close()  # Use close instead of save
            b.seek(0)
            # Send the data as an HTTP response
            response = HttpResponse(
                b,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="data.xlsx"'
            return response
    else:
        return HttpResponse(status=405)