import requests

token = "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI1NTcwMzQyNyIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc2MjQwMjI4NywiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiMTgxMDQ2MjAyNDMiLCJvcGVuSWQiOm51bGwsInV1aWQiOiJkYTExZDAyNy1mNTAwLTQ2ODItODI4MC00MjM2MmUwOTYxNGQiLCJlbWFpbCI6IiIsImV4cCI6MTc2MzYxMTg4N30.qbfFYoV4NTFFuqC_VeDU67kiZh3GWmaDKyPUkxlj0l7uWv1S8yonzOI2SFzA-A5RKaq4rFy4Cel7Efr-mkzQ7g"
url = f"https://mineru.net/api/v4/extract/task/10ab84cd-09ea-44ca-aef9-70990e36f39c"
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

res = requests.get(url, headers=header)
print(res.status_code)
print(res.json())
print(res.json()["data"])