# this is views.py for backend logic of various pages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import views as auth_views, login, authenticate
from companymaster.models import Filing, Company, Exchange, Fundparty, Currency, Country, PDFPage, PDFModel
from django.contrib.auth.decorators import login_required
import json
import datetime
from django.http import JsonResponse, HttpResponseRedirect
from companymaster.form import CompanyInfoForm, FundPartyForm, OfferingDetail, OffershareDetail, FinancialDetail, CompanySearch
from companytransaction.models import CompanyExchange, CompanyOfferingStatus, CompanyCountry, CompanyOfferings, IndustryCompany, CompanyOfferingShares, CompanyFinancial, CompanyOfferingFeesExpense, Offering, CompanyRepresentative, CompanyKeyshareholder, FundPartyUnderwriter, CompanyCurrency, CompanyContact, CompanyFiling, FundpartyCompanyCouncel, FundpartyTransferAgent, FundpartyAuditor, FundpartyUnderwiterCouncel, CompanyRepresentative, FundpartyLeadUnderwiter, CompanyIndustry

from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Sum, F, Count
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from django.core.files.storage import FileSystemStorage

import random
# ADDING PDF


@csrf_exempt
def addPDF(request):
    """
    This method is used for adding a new fund party in database.
    Parameters:
        request: http POST request
    """
    if request.POST.get('action') == 'add-pdf':
        filename = request.POST.get('filename')
        uri = request.POST.get('uri')
        file = request.FILES.get('file')
        print(uri)
        print('-------------------')
        print(file)
        if file:
            fs = FileSystemStorage(location='companymaster/static/asset/pdf')
            saved_file = fs.save(
                filename+'-'+str(request.user.id)+'.pdf', file)
            fileurl = fs.url(saved_file)
            pdf = PDFModel(path='/static/asset/pdf/' +
                           fileurl, filename=filename)
        else:
            pdf = PDFModel(path=uri, filename=filename)

        pdf.save()
    return render(request, 'companymaster/addcompany.html')


def home(request):
    """
    This method renders the summary page for home url
    """
    return render(request, 'companymaster/summary.html')


def login(request):
    """
    This method renders the login page
    """
    return render(request, 'companymaster/login.html')


def summary(request):
    # 17/5/21
    """
    This method renders the summary page
    """

    years = []
    summary = []
    company = Company.objects.all()
    for i in company:
        year = str(i.created_date)[0:4]
        if not year in years:
            years.append(year)
    for year in years:
        company_countries = CompanyCountry.objects.filter(
            created_date__year=year)

        for company_country in company_countries:
            country = Country.objects.get(id=company_country.country.id)
            if(len(summary) >= 1):

                for s in summary:

                    if s['year'] == year:

                        if country.country_symbol in s:
                            s[country.country_symbol] += 1

                        else:
                            s[country.country_symbol] = 1

                        s['total'] += 1
                    else:
                        summary.append(
                            {'year': year, country.country_symbol: 1, 'total': 1})
            else:
                summary.append(
                    {'year': year, country.country_symbol: 1, 'total': 1})
    # print(summary)
    # print('-------------------')

    company_filter = {}
    for c in company:
        cc = CompanyCountry.objects.get(company=c.id)
        country = Country.objects.get(id=cc.country.id)
        if(Offering.objects.filter(company=c.id, is_deleted=0).exists()):
            offering = Offering.objects.filter(company=c.id).last()
            company_offering = CompanyOfferings.objects.get(
                id=offering.offering.id)
            if(CompanyOfferingShares.objects.filter(
                    company_offering=company_offering.id).exists()):
                offer = CompanyOfferingShares.objects.get(
                    company_offering=1)
                print(offer)
                offer_min = offer.offer_amount_min
                offer_max = offer.offer_amount_max
            else:
                offer_min = None
                offer_max = None

            if country.country_symbol in company_filter:

                company_filter[country.country_symbol].append({
                    "cname": c.company_name,
                    "type": company_offering.offering_type,
                    "offer_min": offer_min,
                    "offer_max": offer_max
                })
            else:
                company_filter[country.country_symbol] = [{
                    "cname": c.company_name,
                    "type": company_offering.offering_type,
                    "offer_min": offer_min,
                    "offer_max": offer_max
                }]

    print(company_filter)

    return render(request, 'companymaster/summary.html', {'name': request.user.username, 'summary': summary, 'company_filter': company_filter})

# for cname in cf:
#                             if(c.company_name in cname):
#                                 pass
#                             else:
#                                 cf[country.country_symbol].append({
#                                     "cname": c.company_name,
#                                     "type": company_offering.offering_type
#                                 })

# def company_search(request):
#     search_form = CompanySearch()
#     company = Company.objects.all()
#     company_with_country = []
#     for i in company:
#         try:
#             company_country = CompanyCountry.objects.filter(company_id=i.id)
#             country_model = Country.objects.filter(
#                 id=company_country.country_id)
#             offering = CompanyOfferingStatus.objects.filter(company_id=i.id)
#             offering_type = Offering.objects.filter(id=offering.id)
#             company_with_country.append(
#                 {"company": i, 'country': country_model, 'offering': offering, 'offering_type': offering_type})
#         except:
#             pass

#     return render(request, 'companymaster/companysearch.html', {'name': request.user.username, 'search_form': search_form, 'company_with_country': company_with_country})


def company_search(request):
    search_form = CompanySearch()
    # company = Company.objects.all()
    # print(company)
    # company_with_country = []
    # for i in company:
    #     company_country = CompanyCountry.objects.filter(company=i.id).first()
    #     if company_country:
    #         country_model = Country.objects.filter(
    #             id=company_country.country_id).first()
    #     offering = CompanyOfferingStatus.objects.filter(company=i.id).first()
    #     if offering:
    #         offering_type = CompanyOfferings.objects.filter(
    #             id=offering.id).first()

    #     company_with_country.append(
    #         {"company": i, 'country': country_model, 'offering': offering, 'offering_type': offering_type})

    # return render(request, 'companymaster/companysearch.html', {'name': request.user.username, 'search_form': search_form, 'company_with_country': company_with_country})
    return render(request, 'companymaster/companysearch.html', {'name': request.user.username, 'search_form': search_form})


@csrf_exempt
def ipo_search(request):
    """
    This function returns the company information to search view depending on the search criteria.
    Paramters:
        request: HTTP request
    """
    # get post data from request
    post_data = json.loads(request.body)
    # convert values to None if they are empty
    post_data = {k: None if not v else v for k, v in post_data.items()}
    print(post_data)
    company_id = post_data.get('company')
    symbol = post_data.get('symbol')
    country = post_data.get('country')
    type_of_offer = post_data.get('type_of_offer')
    cik = post_data.get('cik')
    cusip = post_data.get('cusip')
    isin = post_data.get('isin')
    lei = post_data.get('lei')
    sedol = post_data.get('sedol')
    sic_code = post_data.get('sic_code')

    # create the search query
    query = Q()
    if company_id:
        query &= Q(id=company_id[0])
    if symbol:
        query &= Q(symbol__icontains=symbol)
    if cik:
        query &= Q(cik__icontains=cik)
    if cusip:
        query &= Q(cusip__icontains=cusip)
    if isin:
        query &= Q(isin__icontains=isin)
    if lei:
        query &= Q(lei__icontains=lei)
    if sedol:
        query &= Q(sedol__icontains=sedol)
    if sic_code:
        query &= Q(sic_code__icontains=sic_code)

    # check whether the company exists with the search criteria. IF yes, then proceed else return no data
    if Company.objects.filter(query, is_deleted=0).exists():
        # if the company exists get the required information
        company_info = list(Company.objects.filter(query, is_deleted=0).values(
            'id', 'company_name', 'symbol', 'financial_year_end'))
        print(company_info)
        # get company id
        company_id = company_info[0]['id']
        # get company country
        company_country = CompanyCountry.objects.filter(
            company_id=company_id, is_deleted=0).values_list('country_id__country_name', flat=True)
        if company_country.exists():
            country = company_country[0]
        else:
            country = None
        company_info[0]['country'] = country

        # replace None values
        if company_info[0]['country'] == None:
            company_info[0]['country'] = '-'
        if company_info[0]['financial_year_end'] == None:
            company_info[0]['financial_year_end'] = '-'

        # create mysql engine
        engine = create_engine(
            "mysql+pymysql://sunil:sunil@123@192.168.4.65:3306/dpa_ipopulse_development")
        # get offering information for the searched company
        offering_query = "SELECT o.id,company_id,listing_status,date_of_listing,offering_announcement_date,offering_start_date,offering_end_date,offering_type FROM companytransaction_offering o left join companytransaction_companyofferingstatus s on s.company_offering_id=o.id left join companymaster_listingstatus ls on ls.id=s.listing_status_id left join companymaster_companyofferings co on co.id=o.offering_id where o.is_deleted=0 and s.is_deleted=0 and company_id=" + \
            str(company_id)+" order by snapshot_date desc"
        offering_list = pd.read_sql(offering_query, engine)
        offering_list.drop_duplicates(
            subset=['id'], keep='first', inplace=True)
        offering_list = offering_list.fillna(np.nan).replace(
            [np.nan], ['-']).to_dict(orient='records')

        # return company_info
        return JsonResponse({'company_info': company_info, 'offering_list': offering_list})

    else:
        return JsonResponse({'company_info': None, 'offering_list': None})


def addcompany(request):
    """
    This method renders form for add company page.
    """
    form = CompanyInfoForm()
    return render(request, 'companymaster/addcompany.html', {'name': request.user.username, 'form': form})


@csrf_exempt
def addcompany_update(request):
    """
    This function updates the selected company information.
    Paramters:
        request: HTTP request
    """

    # get post data from request
    post_data = json.loads(request.body)
    # convert values to None if they are empty
    post_data = {k: None if not v else v for k, v in post_data.items()}

    issuer_names = post_data.get('issuer_names')
    no_of_employees = post_data.get('no_of_employees')
    currency = post_data.get('currency')
    establishment = post_data.get('establishment')
    industry = post_data.get('industry')
    country = post_data.get('country')
    business_description = post_data.get('business_description')
    address = post_data.get('address')
    website = post_data.get('website')
    contact_no = post_data.get('contact_no')
    exchange = post_data.get('exchange')
    country_exchange = post_data.get('country_exchange')
    financial = post_data.get('financial')
    symbol = post_data.get('symbol')
    CIK = post_data.get('CIK')
    ISIN = post_data.get('ISIN')
    CUSIP = post_data.get('CUSIP')
    LEI = post_data.get('LEI')
    SEDOL = post_data.get('SEDOL')
    MIC_Seg = post_data.get('MIC_Seg')
    SIC_Code = post_data.get('SIC_Code')
    MIC_Code = post_data.get('MIC_Code')

    # update the company information in companymaster table
    company_info = Company.objects.get(company_name=issuer_names)
    company_info.no_of_employees = no_of_employees
    company_info.year_of_establishment = establishment
    company_info.business_description = business_description
    company_info.financial_year_end = financial
    company_info.symbol = symbol
    company_info.cik = CIK
    company_info.isin = ISIN
    company_info.cusip = CUSIP
    company_info.lei = LEI
    company_info.sedol = SEDOL
    company_info.mic_seg = MIC_Seg
    company_info.sic_code = SIC_Code
    company_info.mic_code = MIC_Code
    company_info.updated_by_id = request.user.id
    company_info.updated_date = datetime.datetime.now()
    company_info.save()

    # get company id
    company_id = company_info.id

    # get company contact related information
    address = post_data.get('address')
    website = post_data.get('website')
    contact = post_data.get('contact_no')
    # check if company contact related record is available in table. if yes, then update else insert new record
    if not CompanyContact.objects.filter(company_id=company_id, is_deleted=0).exists():
        company_contact = CompanyContact(
            company_id=company_id, address=address, phone=contact, website=website, updated_by_id=request.user.id)
        company_contact.save()
    else:
        company_contact = CompanyContact.objects.get(company_id=company_id)
        company_contact.website = website
        company_contact.address = address
        company_contact.phone = contact_no
        company_contact.updated_by_id = request.user.id
        company_contact.updated_date = datetime.datetime.now()
        company_contact.save()

    # check if company exchange related record is available in table. if yes, then update else insert new record
    if not CompanyExchange.objects.filter(company_id=company_id, is_deleted=0).exists():
        company_exchange = CompanyExchange(company_id=company_id, exchange_id=exchange,
                                           exchange_country_id=country_exchange, updated_by_id=request.user.id)
        company_exchange.save()
    else:
        company_exchange = CompanyExchange.objects.get(company_id=company_id)
        company_exchange.exchange_id = exchange
        company_exchange.exchange_country_id = country_exchange
        company_exchange.updated_by_id = request.user.id
        company_exchange.updated_date = datetime.datetime.now()
        company_exchange.save()

    # check if company currency related record is available in table. if yes, then update else insert new record
    if not CompanyCurrency.objects.filter(company_id=company_id, is_deleted=0).exists():
        company_currency = CompanyCurrency(
            company_id=company_id, currency_id=currency, updated_by_id=request.user.id)
        company_currency.save()
    else:
        company_currency = CompanyCurrency.objects.get(company_id=company_id)
        company_currency.currency_id = currency
        company_currency.updated_by_id = request.user.id
        company_currency.updated_date = datetime.datetime.now()
        company_currency.save()

    # check if company country related record is available in table. if yes, then update else insert new record
    if not CompanyCurrency.objects.filter(company_id=company_id, is_deleted=0).exists():
        company_country = CompanyCountry(
            company_id=company_id, country_id=country, updated_by_id=request.user.id)
        company_country.save()
    else:
        company_country = CompanyCountry.objects.get(company_id=company_id)
        company_country.country_id = country
        company_country.updated_by_id = request.user.id
        company_country.updated_date = datetime.datetime.now()
        company_country.save()

    # check if company industry related record is available in table. if yes, then update else insert new record
    if not CompanyIndustry.objects.filter(company_id=company_id, is_deleted=0).exists():
        company_industry = CompanyIndustry(
            company_id=company_id, industry_id=industry, updated_by_id=request.user.id)
        company_industry.save()
    else:
        company_industry = CompanyIndustry.objects.get(company_id=company_id)
        company_industry.industry_id = industry
        company_industry.updated_by_id = request.user.id
        company_industry.updated_date = datetime.datetime.now()
        company_industry.save()

    return JsonResponse({'name': request.user.username, 'company_id': company_id, 'status': 'success'})


def addcompany_updateView(request, company_id, tid):
    """
    This function returns the selected company information to update view.
    Paramters:
        request: HTTP request
        company_id: Company ID whose information needs to be updated
        tid: primary key ID of offering table
    """
    # get company object for the requested company id
    companyData = Company.objects.get(id=company_id)

    # check whether currency related information is present. If yes then get that value else return None
    if CompanyCurrency.objects.filter(company_id=company_id, is_deleted=0).exists():
        currency = CompanyCurrency.objects.get(company_id=company_id).currency
    else:
        currency = None

    # check whether country related information is present. If yes then get that value else return None
    if CompanyCountry.objects.filter(company_id=company_id, is_deleted=0).exists():
        country = CompanyCountry.objects.get(company_id=company_id).country
    else:
        country = None

    # check whether industry related information is present. If yes then get that value else return None
    if CompanyIndustry.objects.filter(company_id=company_id, is_deleted=0).exists():
        industry = CompanyIndustry.objects.get(company_id=company_id).industry
    else:
        industry = None

    # check whether exchange related information is present. If yes then get that value else return None
    if CompanyExchange.objects.filter(company_id=company_id, is_deleted=0).exists():
        ex_query = CompanyExchange.objects.get(company_id=company_id)
        exchange = ex_query.exchange
        exchange_country = ex_query.exchange_country_id
    else:
        exchange = None
        exchange_country = None

    # check whether company contact related information is present. If yes then get that value else return None
    if CompanyContact.objects.filter(company_id=company_id, is_deleted=0).exists():
        contact_query = CompanyContact.objects.get(company_id=company_id)
        website = contact_query.website
        phone = contact_query.phone
        address = contact_query.address
    else:
        website = None
        phone = None
        address = None

    # create a dictionary of all the values
    initialData = {
        "issuer_names": companyData.company_name,

        "no_of_employees": companyData.no_of_employees,
        "business_description": companyData.business_description,
        "financial": companyData.financial_year_end,
        "MIC_Code": companyData.mic_code,
        "SIC_Code": companyData.sic_code,
        "no_of_employees": companyData.no_of_employees,
        "establishment": companyData.year_of_establishment,
        "symbol": companyData.symbol,
        "CIK": companyData.cik,
        "CUSIP": companyData.cusip,
        "ISIN": companyData.isin,
        "LEI": companyData.lei,
        "SEDOL": companyData.sedol,
        "MIC_Seg": companyData.mic_seg,
        'MIC_Code': companyData.mic_code,
        # check for None value fields (if matching record not present)
        'currency': currency,
        'country': country,
        'industry': industry,
        'website': website,
        'contact_no': phone,
        'address': address,
        'exchange': exchange,
        'country_exchange': exchange_country,
    }
    form = CompanyInfoForm(request.POST or None, initial=initialData)
    return render(request, 'companymaster/addcompany.html', {'name': request.user.username, 'form': form, 'companyID': company_id, 'tid': tid})


def addcompany_2(request):
    """
    This method renders form for fund party page (add-company-2).
    """
    form2 = FundPartyForm
    return render(request, 'companymaster/addcompany_2.html', {'name': request.user.username, 'form2': form2})


def addcompany_3(request):
    """
    This method renders form for various announcement date and status page (add-company-3).
    """
    offerForm = OfferingDetail
    return render(request, 'companymaster/addcompany_3.html', {'name': request.user.username, 'offerForm': offerForm})


def add_offering(request):
    """
    This method renders form for various announcement date and status page (add-company-3).
    """
    offerForm = OfferingDetail
    return render(request, 'companymaster/addcompany_3.html', {'name': request.user.username, 'offerForm': offerForm, 'offering': 'True'})


def add_offering_shares(request):
    """
    This method renders form for various announcement date and status page (add-company-3).
    """
    offerShare = OffershareDetail
    return render(request, 'companymaster/addcompany_4.html', {'name': request.user.username, 'offerShare': offerShare, 'offering': 'True'})


def add_offering_financial(request):
    """
    This method renders form for various announcement date and status page (add-company-3).
    """
    financial = FinancialDetail
    return render(request, 'companymaster/addcompany_5.html', {'name': request.user.username, 'financial': financial, 'offering': 'True'})


def addcompany_2_extraField(request, company_id):
    company_share_holder = CompanyKeyshareholder.objects.filter(
        company=company_id, is_active=True).values('keyshareholders_name', 'description', 'id')
    company_nominee = CompanyRepresentative.objects.filter(
        company=company_id, is_active=True, designation='Director Nominee').values('representative_name', 'description', 'id')
    company_ceo = CompanyRepresentative.objects.filter(
        company=company_id, is_active=True, designation='CEO').values('representative_name', 'description', 'id')
    company_cfo = CompanyRepresentative.objects.filter(
        company=company_id, is_active=True, designation='CFO').values('representative_name', 'description', 'id')
    company_chairmen = CompanyRepresentative.objects.filter(
        company=company_id, designation='Chair. of B. Direc').values('representative_name', 'description', 'id')
    company_director = CompanyRepresentative.objects.filter(
        company=company_id, is_active=True, designation='Director').values('representative_name', 'description', 'id')
    return JsonResponse({'keyshare': list(company_share_holder), 'nominees': list(company_nominee), 'ceo': list(company_ceo), 'cfo': list(company_cfo), 'chairmens': list(company_chairmen), 'directors': list(company_director)})


@csrf_exempt
def addcompany2_update(request):
    """
    This function updates the selected company information.
    Paramters:
        request: HTTP request
    """
    post_data = json.loads(request.body)
    post_data = {k: None if not v else v for k, v in post_data.items()}
    # get post data from request
    company_id = post_data['company'][0]
    lead_underwriter = post_data['lead_underwriter']
    underwriter = post_data['underwriter']
    u_counsel = post_data['u_counsel']
    auditors = post_data['auditors']
    transfer_agent = post_data['transfer_agent']
    comp_counsel = post_data['comp_counsel']
    key_share_holder = post_data['key_share_holder']
    key_share_holder_description = post_data['key_share_holder_description']
    director_nominee = post_data['director_nominee']
    director_nominee_description = post_data['director_nominee_description']
    ceo = post_data['ceo']
    ceo_description = post_data['ceo_description']
    cfo = post_data['cfo']
    cfo_description = post_data['cfo_description']
    chair_dir = post_data['chair_dir']
    chair_dir_description = post_data['chair_dir_description']
    directors = post_data['directors']
    directors_description = post_data['directors_description']
    print(lead_underwriter)
    fundleadold = FundpartyLeadUnderwiter.objects.filter(
        company_id=int(company_id))
    for f in fundleadold:
        f.is_active = False
        f.is_deleted = True
        f.save()
    underwriterold = FundPartyUnderwriter.objects.filter(
        company_id=int(company_id))
    for f in underwriterold:
        f.is_active = False
        f.is_deleted = True
        f.save()

    undercouncilold = FundpartyUnderwiterCouncel.objects.filter(
        company_id=int(company_id))
    for f in undercouncilold:
        f.is_active = False
        f.is_deleted = True
        f.save()
    auditorold = FundpartyAuditor.objects.filter(company_id=int(company_id))
    for f in auditorold:
        f.is_active = False
        f.is_deleted = True
        f.save()
    agentold = FundpartyTransferAgent.objects.filter(
        company_id=int(company_id))
    for f in agentold:
        f.is_active = False
        f.is_deleted = True
        f.save()
    companycoulold = FundpartyCompanyCouncel.objects.filter(
        company_id=int(company_id))
    for f in companycoulold:
        f.is_active = False
        f.is_deleted = True
        f.save()
    keyold = CompanyKeyshareholder.objects.filter(
        company_id=int(company_id))
    for f in keyold:
        f.is_active = False
        f.is_deleted = True
        f.save()
    rold = CompanyRepresentative.objects.filter(
        company_id=int(company_id))
    for f in rold:
        f.is_active = False
        f.is_deleted = True
        f.save()

    print(CompanyRepresentative.objects.filter(company_id=int(company_id)))
    print('----------------------------')
    print(directors)
    for lead in lead_underwriter:
        if lead not in (None, ''):
            lead_r = FundpartyLeadUnderwiter(company_id=int(
                company_id), fundparty_id=int(lead), updated_by_id=request.user.id)
            lead_r.save()

    for writer in underwriter:
        if writer not in (None, ''):
            w = FundPartyUnderwriter(company_id=int(company_id), fundparty_id=int(
                writer), updated_by_id=request.user.id)
            w.save()

    for councel in u_counsel:
        if councel not in (None, ''):
            uc = FundpartyUnderwiterCouncel(company_id=int(
                company_id), fundparty_id=int(councel), updated_by_id=request.user.id)
            uc.save()

    for auditor in auditors:
        if auditor not in (None, ''):
            a = FundpartyAuditor(company_id=int(company_id), fundparty_id=int(
                auditor), updated_by_id=request.user.id)
            a.save()

    for agent in transfer_agent:
        if agent not in (None, ''):
            ta = FundpartyTransferAgent(company_id=int(
                company_id), fundparty_id=int(agent), updated_by_id=request.user.id)
            ta.save()

    for comp in comp_counsel:
        if comp not in (None, ''):
            cc = FundpartyCompanyCouncel(company_id=int(
                company_id), fundparty_id=int(comp), updated_by_id=request.user.id)
            cc.save()

    for key, desp in zip(key_share_holder, key_share_holder_description):
        if key not in (None, ''):
            ks = CompanyKeyshareholder(company_id=int(
                company_id), keyshareholders_name=key, description=desp, updated_by_id=request.user.id)
            ks.save()

    for nominee, desp in zip(director_nominee, director_nominee_description):
        if nominee not in (None, ''):
            n = CompanyRepresentative(company_id=int(company_id), representative_name=nominee,
                                      description=desp, designation='Director Nominee', updated_by_id=request.user.id)
            n.save()

    for ceo_name, desp in zip(ceo, ceo_description):
        if ceo_name not in (None, ''):
            c = CompanyRepresentative(company_id=int(company_id), representative_name=ceo_name,
                                      description=desp, designation='CEO', updated_by_id=request.user.id)
            c.save()

    for cfo_name, desp in zip(cfo, cfo_description):
        if cfo_name not in (None, ''):
            cf = CompanyRepresentative(company_id=int(company_id), representative_name=cfo_name,
                                       description=desp, designation='CFO', updated_by_id=request.user.id)
            cf.save()

    for m, desp in zip(chair_dir, chair_dir_description):
        if m not in (None, ''):
            cd = CompanyRepresentative(company_id=int(company_id), representative_name=m,
                                       description=desp, designation='Chair. of B. Direc', updated_by_id=request.user.id)
            cd.save()

    for director, desp in zip(directors, directors_description):
        if director not in (None, ''):
            d = CompanyRepresentative(company_id=int(company_id), representative_name=director,
                                      description=desp, designation='Director', updated_by_id=request.user.id)
            d.save()

    return JsonResponse({'name': request.user.username, 'company_id': company_id, 'status': 'success'})


def addcompany_2_updateView(request, company_id):

    lead = FundpartyLeadUnderwiter.objects.filter(company=company_id).first()
    writer = FundPartyUnderwriter.objects.filter(company=company_id).first()
    councel = FundpartyUnderwiterCouncel.objects.filter(
        company=company_id).first()
    auditor = FundpartyAuditor.objects.filter(company=company_id).first()
    agent = FundpartyTransferAgent.objects.filter(company=company_id).first()
    comp = FundpartyCompanyCouncel.objects.filter(company=company_id).first()
    company_share_holder = CompanyKeyshareholder.objects.filter(
        company=company_id, is_active=True).first()
    company_nominee = CompanyRepresentative.objects.filter(
        company=company_id, is_active=True,  designation='Director Nominee').first()
    company_ceo = CompanyRepresentative.objects.filter(
        company=company_id, is_active=True,  designation='CEO').first()
    company_cfo = CompanyRepresentative.objects.filter(
        company=company_id, is_active=True,  designation='CFO').first()
    company_chairmen = CompanyRepresentative.objects.filter(
        company_id=company_id, is_active=True,  designation='Chair. of B. Direc').first()
    company_director = CompanyRepresentative.objects.filter(
        company=company_id, is_active=True,  designation='Director').first()
    print(company_chairmen)
    initialData = {
        'company': company_id,
        'lead_underwriter': lead.fundparty,
        'underwriter': writer.fundparty,
        'u_counsel': councel.fundparty,
        'auditors': auditor.fundparty,
        'transfer_agent': agent.fundparty,
        'comp_counsel': comp.fundparty,
        'key_share_holder': company_share_holder.keyshareholders_name,
        'key_share_holder_description': company_share_holder.description,
        'director_nominee': company_nominee.representative_name,
        'director_nominee_description': company_nominee.description,
        'ceo': company_ceo.representative_name,
        'ceo_description': company_ceo.description,
        'cfo': company_cfo.representative_name,
        'cfo_description': company_cfo.description,
        'chair_dir': company_chairmen.representative_name,
        'chair_dir_description': company_chairmen.description,
        'directors': company_director.representative_name,
        'directors_description': company_director.description,
    }

    form2 = FundPartyForm(request.POST or None, initial=initialData)

    return render(request, 'companymaster/addcompany_2_update.html', {'name': request.user.username, 'form2': form2, 'companyID': company_id, })


def addcompany_3_updateView(request, company_id, tid):
    """
    This function returns the selected company status information to update view.
    Paramters:
        request: HTTP request
        company_id: Company ID whose information needs to be updated
        tid: primary key ID of offering table
    """
    # check whether requested company and offering mapping record is available in database. If yes then get the offering status related information else return empty form.
    if Offering.objects.filter(id=tid, is_deleted=0).exists():
        offering = Offering.objects.get(id=tid)
        offering_id = offering.offering_id
        company_offering_id = offering.id
        # get the latest record (using last()) of company and offering mapping
        if CompanyOfferingStatus.objects.filter(company_offering_id=company_offering_id, is_deleted=0).exists():
            offering_status = CompanyOfferingStatus.objects.filter(
                company_offering_id=company_offering_id, is_deleted=0).latest('snapshot_date')

            # convert offering_announcement_date to date proper date format is it is present
            offering_announcement_date = offering_status.offering_announcement_date
            if offering_announcement_date is not None:
                offering_announcement_date = datetime.datetime.strptime(
                    str(offering_status.offering_announcement_date), '%Y-%m-%d').strftime('%m/%d/%Y')

            # convert offering_price_announcement_date to date proper date format is it is present
            offering_price_announcement_date = offering_status.offering_price_announcement_date
            if offering_price_announcement_date is not None:
                offering_price_announcement_date = datetime.datetime.strptime(str(
                    offering_status.offering_price_announcement_date), '%Y-%m-%d').strftime('%m/%d/%Y')

            # convert offering_start_date to date proper date format is it is present
            offering_start_date = offering_status.offering_start_date
            if offering_start_date is not None:
                offering_start_date = datetime.datetime.strptime(
                    str(offering_status.offering_start_date), '%Y-%m-%d').strftime('%m/%d/%Y')

            # convert offering_end_date to date proper date format is it is present
            offering_end_date = offering_status.offering_end_date
            if offering_end_date is not None:
                offering_end_date = datetime.datetime.strptime(
                    str(offering_status.offering_end_date), '%Y-%m-%d').strftime('%m/%d/%Y')

            # convert share_issue_date to date proper date format is it is present
            share_issue_date = offering_status.share_issue_date
            if share_issue_date is not None:
                share_issue_date = datetime.datetime.strptime(
                    str(offering_status.share_issue_date), '%Y-%m-%d').strftime('%m/%d/%Y')

            # convert date_of_listing to date proper date format is it is present
            date_of_listing = offering_status.date_of_listing
            if date_of_listing is not None:
                date_of_listing = datetime.datetime.strptime(
                    str(offering_status.date_of_listing), '%Y-%m-%d').strftime('%m/%d/%Y')

            # convert snapshot_date to date proper date format is it is present
            snapshot_date = offering_status.snapshot_date
            if snapshot_date is not None:
                snapshot_date = datetime.datetime.strptime(
                    str(offering_status.snapshot_date), '%Y-%m-%d').strftime('%m/%d/%Y')

            # convert withdrawn_date to date proper date format is it is present
            withdrawn_date = offering_status.withdrawn_date
            if withdrawn_date is not None:
                withdrawn_date = datetime.datetime.strptime(
                    str(offering_status.withdrawn_date), '%Y-%m-%d').strftime('%m/%d/%Y')

            # convert postpone_date to date proper date format is it is present
            postpone_date = offering_status.postpone_date
            if postpone_date is not None:
                postpone_date = datetime.datetime.strptime(
                    str(offering_status.postpone_date), '%Y-%m-%d').strftime('%m/%d/%Y')

            # create a dictionary of all the values
            initialData = {
                "company": company_id,
                "choice": offering_id,
                "use_of_Proceeds": offering_status.use_of_proceeds,
                "listing_status": offering_status.listing_status,
                "ipo_status": offering_status.IPO_status,
                "offer_status": offering_status.offer_status,
                "type_of_listing": offering_status.type_of_listing,
                "ipo_announcement_dt": offering_announcement_date,
                "ipo_pr_announcement_dt": offering_price_announcement_date,
                "ipo_start_dt": offering_start_date,
                "ipo_end_dt": offering_end_date,
                "share_issue_dt": share_issue_date,
                "date_of_listing": date_of_listing,
                "postpone_date": postpone_date,
                "withdrawn_date": withdrawn_date,
                "snapshot_date": snapshot_date,
            }

            form = OfferingDetail(request.POST or None, initial=initialData)

            return render(request, 'companymaster/addcompany_3.html', {'name': request.user.username, 'offerForm': form, 'companyID': company_id, 'tid': tid})

        else:
            form = OfferingDetail
            return render(request, 'companymaster/addcompany_3.html', {'name': request.user.username, 'companyID': company_id, 'offerForm': form, 'tid': tid})

    else:
        form = OfferingDetail
        return render(request, 'companymaster/addcompany_3.html', {'name': request.user.username, 'companyID': company_id, 'offerForm': form, 'tid': tid})


def addcompany_4(request):
    """
    This method renders form for offer shares page (add-company-4).
    """
    offerShare = OffershareDetail
    return render(request, 'companymaster/addcompany_4.html', {'name': request.user.username, 'offerShare': offerShare})


def addcompany_4_updateView(request, company_id, tid):
    """
    This function returns the selected company offering shares and expenses information to update view.
    Paramters:
        request: HTTP request
        company_id: Company ID whose information needs to be updated
        tid: primary key ID of offering table
    """
    if Offering.objects.filter(id=tid, is_deleted=0).exists():
        offering = Offering.objects.get(id=tid)
        offering_id = offering.offering_id
    else:
        offering_id = None

    if CompanyOfferingFeesExpense.objects.filter(company_offering_id=tid, is_deleted=0).exists():
        offering_fees_expense = CompanyOfferingFeesExpense.objects.filter(
            company_offering_id=tid, is_deleted=0).latest('snapshot_date')
        registeration_fee = offering_fees_expense.registeration_fee
        type_of_equity_instrument = offering_fees_expense.type_of_equity_instrument
        security_description = offering_fees_expense.security_description
        warants_issued = offering_fees_expense.warants_issued
        ex_price_of_warants = offering_fees_expense.ex_price_of_warants
        total_offering_expense = offering_fees_expense.total_offering_expense
        legal_fees_expenses = offering_fees_expense.legal_fees_expenses
        security_parvalue = offering_fees_expense.security_parvalue
        currency_id = offering_fees_expense.currency_id
    else:
        registeration_fee = None
        type_of_equity_instrument = None
        security_description = None
        warants_issued = None
        ex_price_of_warants = None
        total_offering_expense = None
        legal_fees_expenses = None
        security_parvalue = None
        currency_id = None

    if CompanyOfferingShares.objects.filter(company_offering_id=tid, is_deleted=0).exists():
        company_offering_shares = CompanyOfferingShares.objects.filter(
            company_offering_id=tid, is_deleted=0).latest('snapshot_date')

        shares_offered_min = company_offering_shares.shares_offered_min
        shares_offered_max = company_offering_shares.shares_offered_max
        strategic_shares_offered = company_offering_shares.strategic_shares_offered
        additional_shares_offered_aboveIPO = company_offering_shares.additional_shares_offered_aboveIPO
        offer_amount_min = company_offering_shares.offer_amount_min
        offer_amount_max = company_offering_shares.offer_amount_max
        price_range_min = company_offering_shares.price_range_min
        price_range_max = company_offering_shares.price_range_max
        underwriting_discount = company_offering_shares.underwriting_discount
        proceeds_after_expense = company_offering_shares.proceeds_after_expense
        shares_outstanding = company_offering_shares.shares_outstanding
        shareholder_shares_offered = company_offering_shares.shareholder_shares_offered
        lockup_period = company_offering_shares.lockup_period
        number_of_shares_issued = company_offering_shares.number_of_shares_issued
        strategic_sale_offer_that_were_issued = company_offering_shares.strategic_sale_offer_that_were_issued
        number_of_greenshoe_shares_issued = company_offering_shares.number_of_greenshoe_shares_issued
        shares_overalloted = company_offering_shares.shares_overalloted
        prospectus_link = company_offering_shares.prospectus_link

        # convert lockup_expiration_date to date proper date format is it is present
        lockup_expiration_date = company_offering_shares.lockup_expiration_date
        if lockup_expiration_date is not None:
            lockup_expiration_date = datetime.datetime.strptime(str(
                company_offering_shares.lockup_expiration_date), '%Y-%m-%d').strftime('%m/%d/%Y')

        # convert quiet_period_expiration_date to date proper date format is it is present
        quiet_period_expiration_date = company_offering_shares.quiet_period_expiration_date
        if quiet_period_expiration_date is not None:
            quiet_period_expiration_date = datetime.datetime.strptime(str(
                company_offering_shares.quiet_period_expiration_date), '%Y-%m-%d').strftime('%m/%d/%Y')

        # convert greenshoe_option_exercise_date to date proper date format is it is present
        greenshoe_option_exercise_date = company_offering_shares.greenshoe_option_exercise_date
        if greenshoe_option_exercise_date is not None:
            greenshoe_option_exercise_date = datetime.datetime.strptime(str(
                company_offering_shares.greenshoe_option_exercise_date), '%Y-%m-%d').strftime('%m/%d/%Y')

        # convert snapshot_date to date proper date format is it is present
        offering_shares_snapshot_date = company_offering_shares.snapshot_date
        if offering_shares_snapshot_date is not None:
            offering_shares_snapshot_date = datetime.datetime.strptime(
                str(company_offering_shares.snapshot_date), '%Y-%m-%d').strftime('%m/%d/%Y')

    else:
        shares_offered_min = None
        shares_offered_max = None
        strategic_shares_offered = None
        additional_shares_offered_aboveIPO = None
        offer_amount_min = None
        offer_amount_max = None
        price_range_min = None
        price_range_max = None
        underwriting_discount = None
        proceeds_after_expense = None
        shares_outstanding = None
        shareholder_shares_offered = None
        lockup_period = None
        number_of_shares_issued = None
        strategic_sale_offer_that_were_issued = None
        number_of_greenshoe_shares_issued = None
        shares_overalloted = None
        prospectus_link = None
        lockup_expiration_date = None
        quiet_period_expiration_date = None
        greenshoe_option_exercise_date = None
        offering_shares_snapshot_date = None

    initialData = {
        "company": company_id,
        "offering": offering_id,
        "shares_offered_min": shares_offered_min,
        "shares_offered_max": shares_offered_max,
        "strategic_shares_off": strategic_shares_offered,
        "add_sh_off_above_ipo": additional_shares_offered_aboveIPO,
        "offer_amount_min": offer_amount_min,
        "offer_amount_max": offer_amount_max,
        "price_range_min": price_range_min,
        "price_range_max": price_range_max,
        "underwriting_discount": underwriting_discount,
        "proceeds_after_expense": proceeds_after_expense,
        "shares_outstanding": shares_outstanding,
        "sh_shares_offered": shareholder_shares_offered,
        "lockup_period": lockup_period,
        "no_of_shares_issued": number_of_shares_issued,
        "shares_after_str": strategic_sale_offer_that_were_issued,
        "no_of_grreenshoe_sh_iss": number_of_greenshoe_shares_issued,
        "shares_overalloted": shares_overalloted,
        "prospectus_link": prospectus_link,
        "lockup_expiration": lockup_expiration_date,
        "quiet_period_expiration": quiet_period_expiration_date,
        "greenshoe_opt_exercise_dt": greenshoe_option_exercise_date,
        "snapshot_date": offering_shares_snapshot_date,
        # fees expense related fields
        "registration_fee": registeration_fee,
        "typ_of_eq_instrument": type_of_equity_instrument,
        "security_description": security_description,
        "warants_issued": warants_issued,
        "ex_price_of_warants": ex_price_of_warants,
        "total_offering_exp": total_offering_expense,
        "legal_fees_exp": legal_fees_expenses,
        "security_parvalue": security_parvalue,
        "security_parvalue_curr": currency_id,
    }

    offerShare = OffershareDetail(request.POST or None, initial=initialData)

    return render(request, 'companymaster/addcompany_4.html', {'name': request.user.username, 'offerShare': offerShare, 'companyID': company_id, 'tid': tid})


def addcompany_5(request):
    """
    This method renders form for offer financials page (add-company-5).
    """
    financial = FinancialDetail
    return render(request, 'companymaster/addcompany_5.html', {'name': request.user.username, 'financial': financial})


def addcompany_5_updateView(request, company_id, tid):
    """
    This function returns the selected company offering shares and expenses information to update view.
    Paramters:
        request: HTTP request
        company_id: Company ID whose information needs to be updated
        tid: primary key ID of offering table
    """
    if Offering.objects.filter(id=tid, is_deleted=0).exists():
        offering = Offering.objects.get(id=tid)
        offering_id = offering.offering_id
    else:
        offering_id = None

    if CompanyFinancial.objects.filter(company_offering_id=tid, is_deleted=0).exists():
        company_financial = CompanyFinancial.objects.filter(
            company_offering_id=tid, is_deleted=0).latest('snapshot_date')

        # convert snapshot_date to date proper date format is it is present
        snapshot_date = company_financial.snapshot_date
        if snapshot_date is not None:
            snapshot_date = datetime.datetime.strptime(
                str(company_financial.snapshot_date), '%Y-%m-%d').strftime('%m/%d/%Y')

        initialData = {
            "company": company_id,
            "offering": offering_id,
            "date": snapshot_date,
            "revenue": company_financial.revenue,
            "net_income": company_financial.net_income,
            "ebit": company_financial.ebit,
            "ebidta": company_financial.ebitda,
            "y_o_y_growth": company_financial.y_o_y_growth,
            "last_12_month_sales": company_financial.last_12_months_sales,
            "last_24_month_sales": company_financial.last_24_months_sales,
            "total_assets": company_financial.total_assets,
            "total_liabilities": company_financial.total_liabilities,
            "cash": company_financial.cash,
            "debt": company_financial.debt,
            "equity": company_financial.equity,
        }

        form = FinancialDetail(request.POST or None, initial=initialData)
        return render(request, 'companymaster/addcompany_5.html', {'name': request.user.username, 'financial': form, 'companyID': company_id, 'tid': tid})

    else:
        initialData = {
            "company": company_id,
            "offering": offering_id,
            "date": None,
            "revenue": None,
            "net_income": None,
            "ebit": None,
            "ebidta": None,
            "y_o_y_growth": None,
            "last_12_month_sales": None,
            "last_24_month_sales": None,
            "total_assets": None,
            "total_liabilities": None,
            "cash": None,
            "debt": None,
            "equity": None,
        }
        form = FinancialDetail
        return render(request, 'companymaster/addcompany_5.html', {'name': request.user.username, 'financial': form, 'companyID': company_id, 'tid': tid})


def addcompany_view(request):
    """
    This method is called for showing the overview page of recently added company by the current logged in user.
    Parameters:
        request: http GET request
    """
    company = Company.objects.filter(
        updated_by=request.user.id, is_deleted=0).last()
    print(company)
    CompanyContact_detail = CompanyContact.objects.filter(
        company_id=company.id, updated_by=request.user.id, is_deleted=0).last()
    CompanyCurrency_detail = CompanyCurrency.objects.filter(
        company_id=company.id, updated_by=request.user.id, is_deleted=0).last()
    CompanyCountry_detail = CompanyCountry.objects.filter(
        company_id=company.id, updated_by=request.user.id, is_deleted=0).last()
    CompanyIndustry_detail = CompanyIndustry.objects.filter(
        company_id=company.id, updated_by=request.user.id, is_deleted=0).last()
    CompanyExchange_detail = CompanyExchange.objects.filter(
        company_id=company.id, updated_by=request.user.id, is_deleted=0).last()
    # get company_offering_id from Offering transaction table to filter in other offering shares, finance and fees related tables
    Offering_detail = Offering.objects.filter(
        company_id=company.id, is_deleted=0).last()
    company_offering_id = Offering_detail.id
    # This is for offering detail page
    offering_status = CompanyOfferingStatus.objects.filter(
        company_offering_id=company_offering_id, is_deleted=0).last()
    # This is for offering share page
    CompanyOfferingShares_detail = CompanyOfferingShares.objects.filter(
        company_offering_id=company_offering_id, is_deleted=0).last()
    CompanyOfferingFeesExpense_detail = CompanyOfferingFeesExpense.objects.filter(
        company_offering_id=company_offering_id, is_deleted=0).last()
    # This is for offering Financial
    CompanyFinancial_detail = CompanyFinancial.objects.filter(
        company_offering_id=company_offering_id, is_deleted=0).last()
    # Fund Party and Management Page
    fundparty_lead_underwriter = FundpartyLeadUnderwiter.objects.filter(
        company_id=company.id, is_deleted=0)
    fundparty_underwriter = FundPartyUnderwriter.objects.filter(
        company_id=company.id, is_deleted=0)
    fundparty_underwriter_councel = FundpartyUnderwiterCouncel.objects.filter(
        company_id=company.id, is_deleted=0)
    fundparty_auditor = FundpartyAuditor.objects.filter(
        company_id=company.id, is_deleted=0)
    fundparty_transfer = FundpartyTransferAgent.objects.filter(
        company_id=company.id, is_deleted=0)
    fundparty_company_councel = FundpartyCompanyCouncel.objects.filter(
        company_id=company.id, is_deleted=0)
    keyshareholder = CompanyKeyshareholder.objects.filter(
        company_id=company.id, is_deleted=0)
    company_representative = CompanyRepresentative.objects.filter(
        company_id=company.id, is_deleted=0)

    context = {'name': request.user.username, 'company': company, 'offering_status': offering_status, 'Offering_detail': Offering_detail, 'CompanyOfferingShares_detail': CompanyOfferingShares_detail, 'CompanyOfferingFeesExpense_detail': CompanyOfferingFeesExpense_detail, 'CompanyFinancial_detail': CompanyFinancial_detail, 'CompanyContact_detail': CompanyContact_detail, 'CompanyCurrency_detail': CompanyCurrency_detail, 'CompanyCountry_detail': CompanyCountry_detail, 'CompanyIndustry_detail': CompanyIndustry_detail,
               'keyshareholder': keyshareholder,
               'fundparty_lead_underwriter': fundparty_lead_underwriter,
               'company_representative': company_representative,
               'fundparty_underwriter': fundparty_underwriter,
               'fundparty_underwriter_councel': fundparty_underwriter_councel,
               'fundparty_auditor': fundparty_auditor,
               'fundparty_transfer': fundparty_transfer,
               'fundparty_company_councel': fundparty_company_councel,
               'CompanyExchange_detail': CompanyExchange_detail,
               }
    return render(request, 'companymaster/addcompany_view.html', context)


def addcompany_view_byID(request, company):
    """
    This method is called for showing the overview page for a company.
    Parameters:
        request: http GET request
        company (int): company-offering mapping id from companytransaction_offering (primary key) table
    """
    # get company_offering_id from Offering transaction table to filter in other offering shares, finance and fees related tables
    company_offering_id = company
    Offering_detail = Offering.objects.filter(
        id=company_offering_id, is_deleted=0).last()
    # get company id to get company related details
    company_id = Offering_detail.company_id
    # get company related information from company_id
    company = Company.objects.filter(id=company_id).last()
    CompanyContact_detail = CompanyContact.objects.filter(
        company_id=company_id, is_deleted=0).last()
    CompanyCurrency_detail = CompanyCurrency.objects.filter(
        company_id=company_id, is_deleted=0).last()
    CompanyCountry_detail = CompanyCountry.objects.filter(
        company_id=company_id, is_deleted=0).last()
    CompanyIndustry_detail = CompanyIndustry.objects.filter(
        company_id=company_id, is_deleted=0).last()
    CompanyExchange_detail = CompanyExchange.objects.filter(
        company_id=company_id, is_deleted=0).last()
    # Fund Party and Management Page
    fundparty_lead_underwriter = FundpartyLeadUnderwiter.objects.filter(
        company_id=company_id, is_deleted=0)
    fundparty_underwriter = FundPartyUnderwriter.objects.filter(
        company_id=company_id, is_deleted=0)
    fundparty_underwriter_councel = FundpartyUnderwiterCouncel.objects.filter(
        company_id=company_id, is_deleted=0)
    fundparty_auditor = FundpartyAuditor.objects.filter(
        company_id=company_id, is_deleted=0)
    fundparty_transfer = FundpartyTransferAgent.objects.filter(
        company_id=company_id, is_deleted=0)
    fundparty_company_councel = FundpartyCompanyCouncel.objects.filter(
        company_id=company_id, is_deleted=0)
    keyshareholder = CompanyKeyshareholder.objects.filter(
        company_id=company_id, is_deleted=0)
    company_representative = CompanyRepresentative.objects.filter(
        company_id=company_id, is_deleted=0)
    # This is for offering detail page
    offering_status = CompanyOfferingStatus.objects.filter(
        company_offering_id=company_offering_id, is_deleted=0).last()
    # This is for offering share page
    CompanyOfferingShares_detail = CompanyOfferingShares.objects.filter(
        company_offering_id=company_offering_id, is_deleted=0).last()
    CompanyOfferingFeesExpense_detail = CompanyOfferingFeesExpense.objects.filter(
        company_offering_id=company_offering_id, is_deleted=0).last()
    # This is for offering Financial
    CompanyFinancial_detail = CompanyFinancial.objects.filter(
        company_offering_id=company_offering_id, is_deleted=0).last()
    context = {'name': request.user.username, 'company': company, 'offering_status': offering_status, 'Offering_detail': Offering_detail, 'CompanyOfferingShares_detail': CompanyOfferingShares_detail, 'CompanyOfferingFeesExpense_detail': CompanyOfferingFeesExpense_detail, 'CompanyFinancial_detail': CompanyFinancial_detail, 'CompanyContact_detail': CompanyContact_detail, 'CompanyCurrency_detail': CompanyCurrency_detail, 'CompanyCountry_detail': CompanyCountry_detail, 'CompanyIndustry_detail': CompanyIndustry_detail,
               'keyshareholder': keyshareholder,
               'fundparty_lead_underwriter': fundparty_lead_underwriter,
               'company_representative': company_representative,
               'fundparty_underwriter': fundparty_underwriter,
               'fundparty_underwriter_councel': fundparty_underwriter_councel,
               'fundparty_auditor': fundparty_auditor,
               'fundparty_transfer': fundparty_transfer,
               'fundparty_company_councel': fundparty_company_councel,
               'CompanyExchange_detail': CompanyExchange_detail,
               }
    return render(request, 'companymaster/addcompany_view.html', context)


def view_report(request):
    return render(request, 'companymaster/view_report.html', {'name': request.user.username})


@csrf_exempt
def addfundparty(request):
    """
    This method is used for adding a new fund party in database.
    Parameters:
        request: http POST request
    """
    post_data = json.loads(request.body)
    fund = Fundparty(company_name=post_data['fund'])
    fund.save()
    return render(request, 'companymaster/addcompany_2.html')


@csrf_exempt
def review(request):
    """
    This method is used for updating is_reviewed flag for a company offering. 
    Post data: 
        company_offering_id: company offering mapping id (from companytransaction_offering table)
        review_flag: 0 means record has been sent for review so set its value to 0. 1 means record is reviewed so set its value to 1
    Parameters:
        request: http POST request
    """
    post_data = json.loads(request.body)
    try:
        company_offering = Offering.objects.get(
            id=post_data['company_offering_id'])
        company_offering.is_reviewed = post_data['review_flag']
        company_offering.save()
        return JsonResponse({'name': request.user.username, 'status': 'success'})
    except Exception as e:
        print("Error in review: "+str(e))
        return JsonResponse({'name': request.user.username, 'status': 'failure'})


@csrf_exempt  # this @csrf_exemp is useful for submit form
def company_details(request):
    """
    This method is used for getting company information.
    Parameters:
        request: http GET request
    """
    company = Company.objects.all()  # getting everything from company model
    container_company = []  # this array to append all detail page data
    if company:
        for i in company:
            # passing company id to companycountry model
            company_country = CompanyCountry.objects.get(id=i.id)
            country = Country.objects.get(
                id=company_country.country_id)  # retrieving country
            # appending company and country to array
            container_company.append({'company': i, 'country': country})
    return render(request, 'companymaster/company_details.html', {'name': request.user.username, 'company': container_company})


@csrf_exempt
def quality_view(request):
    # to display the list of countries in dropdown select
    # country = Country.objects.all()
    country = Country.objects.filter(
        country_name__in=['Canada', 'United States of America', 'United Kingdom'])
    # get count of reviewed records
    reviewed_count_query = Offering.objects.filter(is_reviewed=1, is_deleted=0).values(
        'is_reviewed').annotate(total=Count('is_reviewed'))
    if len(reviewed_count_query) != 0:
        reviewed_count = reviewed_count_query[0]['total']
    else:
        reviewed_count = 0
    # get count of non reviewed records
    unreviewed_count_query = Offering.objects.filter(is_reviewed=0, is_deleted=0).values(
        'is_reviewed').annotate(total=Count('is_reviewed'))
    if len(unreviewed_count_query) != 0:
        unreviewed_count = unreviewed_count_query[0]['total']
    else:
        unreviewed_count = 0
    # get count of total records
    total_count_query = Offering.objects.filter(is_deleted=0).values(
        'is_reviewed').annotate(total=Count('is_reviewed'))
    if len(total_count_query) != 0:
        total_count = total_count_query[0]['total']
    else:
        total_count = 0

    # default country
    selected_country = 1  # United States
    # empty array to append filtered records
    filter_company = []
    # filter by selected country, but only on a POST
    if request.method == "POST":
        selected_country = request.POST.get("country")
        filter_company_id = CompanyCountry.objects.filter(
            country_id=selected_country, is_deleted=0).values_list('company_id', flat=True)
        filtered_companies = Offering.objects.filter(
            company_id__in=filter_company_id, is_reviewed=0, is_deleted=0)
        # get reviewed records
        reviewed_filtered_companies = Offering.objects.filter(
            company_id__in=filter_company_id, is_reviewed=1, is_deleted=0)
    # on page refresh or first visit to page, default country filter will be shown through GET request
    else:
        filter_company_id = CompanyCountry.objects.filter(
            country_id=selected_country, is_deleted=0).values_list('company_id', flat=True)
        filtered_companies = Offering.objects.filter(
            company_id__in=filter_company_id, is_reviewed=0, is_deleted=0)
        # get reviewed records
        reviewed_filtered_companies = Offering.objects.filter(
            company_id__in=filter_company_id, is_reviewed=1, is_deleted=0)

    return render(request, 'companymaster/quality_view.html', {'name': request.user.username, 'country': country,
                                                               'filtered_companies': filtered_companies, 'reviewed_filtered_companies': reviewed_filtered_companies, 'selected_country': int(selected_country), 'reviewed_count': reviewed_count, 'unreviewed_count': unreviewed_count, 'total_count': total_count})

################################### company add pages ####################################


@csrf_exempt
def company_submit_form(request):
    """
    Store company related information in database.
    Parameters:
        request: http POST request
    """
    print("in submit_form")

    post_data = json.loads(request.body)
    post_data = {k: None if not v else v for k, v in post_data.items()}
    issuer_names = post_data['issuer_names']
    if not Company.objects.filter(company_name=issuer_names).exists():
        no_of_employees = post_data['no_of_employees']
        currency = post_data['currency']
        establishment = post_data['establishment']
        industry = post_data['industry']
        country = post_data['country']
        business_description = post_data['business_description']
        address = post_data['address']
        website = post_data['website']
        contact_no = post_data['contact_no']
        exchange = post_data['exchange']
        country_exchange = post_data['country_exchange']
        financial = post_data['financial']
        symbol = post_data['symbol']
        CIK = post_data['CIK']
        ISIN = post_data['ISIN']
        CUSIP = post_data['CUSIP']
        LEI = post_data['LEI']
        SEDOL = post_data['SEDOL']
        MIC_Seg = post_data['MIC_Seg']
        SIC_Code = post_data['SIC_Code']
        MIC_Code = post_data['MIC_Code']

        # 2-6-21
        issuer_names_pdf = post_data['issuer_names_pdf']
        print(issuer_names_pdf)
        issuer_names_page_no = post_data['issuer_names_page_no']
        pdf = PDFModel.objects.filter(path=issuer_names_pdf).first()
        issuer_pdf_page = PDFPage(pdf_id=pdf.id, page_no=issuer_names_page_no)
        issuer_pdf_page.save()

        country_pdf = post_data['country_pdf']
        country_page_no = post_data['country_page_no']
        pdf = PDFModel.objects.filter(path=country_pdf).first()
        country_pdf_page = PDFPage(pdf_id=pdf.id, page_no=country_page_no)
        country_pdf_page.save()

        business_pdf = post_data['business_pdf']
        business_page_no = post_data['business_page_no']
        pdf = PDFModel.objects.filter(path=business_pdf).first()
        business_pdf_page = PDFPage(pdf_id=pdf.id, page_no=business_page_no)
        business_pdf_page.save()

        address_pdf = post_data['address_pdf']
        address_page_no = post_data['address_page_no']
        pdf = PDFModel.objects.filter(path=address_pdf).first()
        address_pdf_page = PDFPage(pdf_id=pdf.id, page_no=address_page_no)
        address_pdf_page.save()

        exchange_pdf = post_data['exchange_pdf']
        exchange_page_no = post_data['exchange_page_no']
        pdf = PDFModel.objects.filter(path=exchange_pdf).first()
        exchange_pdf_page = PDFPage(pdf_id=pdf.id, page_no=exchange_page_no)
        exchange_pdf_page.save()

        symbol_pdf = post_data['symbol_pdf']
        symbol_page_no = post_data['symbol_page_no']
        pdf = PDFModel.objects.filter(path=symbol_pdf).first()
        symbol_pdf_page = PDFPage(pdf_id=pdf.id, page_no=symbol_page_no)
        symbol_pdf_page.save()

        print(pdf.id)
        print(issuer_names_pdf)

        company_info = Company(no_of_employees=no_of_employees, company_name=issuer_names, sic_code=MIC_Seg, mic_seg=SIC_Code, sedol=SEDOL, lei=LEI, cusip=CUSIP, isin=ISIN, cik=CIK, symbol=symbol, mic_code=MIC_Code, financial_year_end=financial, business_description=business_description,
                               year_of_establishment=establishment, updated_by_id=request.user.id, company_name_pdf_id=issuer_pdf_page.id, symbol_pdf_id=symbol_pdf_page.id, exchange_pdf_id=exchange_pdf_page.id, country_pdf_id=country_pdf_page.id, address_pdf_id=address_pdf_page.id, business_description_pdf_id=business_pdf_page.id)
        company_info.save()
        company_id = company_info.id
        print("company id: ", company_info.id)

        address = post_data['address']
        website = post_data['website']
        contact = post_data['contact_no']
        if address is None and website is None and contact is None:
            pass
        else:
            company_contact = CompanyContact(
                company_id=company_id, address=address, phone=contact, website=website, updated_by_id=request.user.id)
            company_contact.save()

        if currency is not None:
            currency_info = CompanyCurrency(
                company_id=company_id, currency_id=currency, updated_by_id=request.user.id)
            currency_info.save()

        if country is not None:
            country_info = CompanyCountry(
                company_id=company_id, country_id=country, updated_by_id=request.user.id)
            country_info.save()

        if industry is not None:
            industry_info = CompanyIndustry(
                company_id=company_id, industry_id=industry, updated_by_id=request.user.id)
            industry_info.save()

        if exchange is not None:
            exchange_info = CompanyExchange(company_id=company_id, exchange_id=exchange,
                                            exchange_country_id=country_exchange, updated_by_id=request.user.id)
            exchange_info.save()

        return JsonResponse({'name': request.user.username, 'new_company_id': company_id, 'status': 'success'})

    else:
        return JsonResponse({'status': 'already exists'})


@csrf_exempt
def fundparty_submit_form(request):
    """
    Store company fundparty related information in database.
    Parameters:
        request: http POST request
    """

    print("in fundparty_submit_form")
    post_data = json.loads(request.body)
    post_data = {k: None if not v else v for k, v in post_data.items()}
    company_id = post_data['company'][0]
    print("company id: ", company_id)

    if company_id is None:
        return render(request, 'companymaster/addcompany_2.html', {'status': 'failure'})

    lead_underwriter = post_data['lead_underwriter']
    underwriter = post_data['underwriter']
    u_counsel = post_data['u_counsel']
    auditors = post_data['auditors']
    transfer_agent = post_data['transfer_agent']
    comp_counsel = post_data['comp_counsel']
    key_share_holder = post_data['key_share_holder']
    key_share_holder_description = post_data['key_share_holder_description']
    director_nominee = post_data['director_nominee']
    director_nominee_description = post_data['director_nominee_description']
    ceo = post_data['ceo']
    ceo_description = post_data['ceo_description']
    cfo = post_data['cfo']
    cfo_description = post_data['cfo_description']
    chair_dir = post_data['chair_dir']
    chair_dir_description = post_data['chair_dir_description']
    directors = post_data['directors']
    directors_description = post_data['directors_description']

    lead_underwriter_pdf = post_data['lead_underwriter_pdf']
    lead_underwriter_page_no = post_data['lead_underwriter_page_no']
    pdf = PDFModel.objects.filter(path=lead_underwriter_pdf).first()
    lead_underwriter_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=lead_underwriter_page_no)
    lead_underwriter_pdf_page.save()

    underwriter_pdf = post_data['underwriter_pdf']

    underwriter_page_no = post_data['underwriter_page_no']
    pdf = PDFModel.objects.filter(path=underwriter_pdf).first()
    underwriter_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=underwriter_page_no)
    underwriter_pdf_page.save()

    auditors_pdf = post_data['auditors_pdf']
    auditors_page_no = post_data['auditors_page_no']
    pdf = PDFModel.objects.filter(path=auditors_pdf).first()
    auditors_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=auditors_page_no)
    auditors_pdf_page.save()

    ceo_pdf = post_data['ceo_pdf']
    ceo_page_no = post_data['ceo_page_no']
    pdf = PDFModel.objects.filter(path=ceo_pdf).first()
    ceo_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=ceo_page_no)
    ceo_pdf_page.save()

    key_share_holder_pdf = post_data['key_share_holder_pdf']
    key_share_holder_page_no = post_data['key_share_holder_page_no']
    pdf = PDFModel.objects.filter(path=key_share_holder_pdf).first()
    key_share_holder_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=key_share_holder_page_no)
    key_share_holder_pdf_page.save()

    lead_r = FundpartyLeadUnderwiter(company_id=int(
        company_id), fundparty_id=int(lead_underwriter), pdf_id=lead_underwriter_pdf_page.id, updated_by_id=request.user.id)
    lead_r.save()

    w = FundPartyUnderwriter(company_id=int(company_id), fundparty_id=int(
        underwriter), updated_by_id=request.user.id, pdf_id=underwriter_pdf_page.id)
    w.save()

    uc = FundpartyUnderwiterCouncel(company_id=int(
        company_id), fundparty_id=int(u_counsel), updated_by_id=request.user.id)
    uc.save()

    a = FundpartyAuditor(company_id=int(company_id), fundparty_id=int(
        auditors), updated_by_id=request.user.id, pdf_id=auditors_pdf_page.id)
    a.save()

    ta = FundpartyTransferAgent(company_id=int(
        company_id), fundparty_id=int(transfer_agent), updated_by_id=request.user.id)
    ta.save()

    cc = FundpartyCompanyCouncel(company_id=int(
        company_id), fundparty_id=int(comp_counsel), updated_by_id=request.user.id)
    cc.save()

    for key, desp in zip(key_share_holder, key_share_holder_description):
        if key not in (None, ''):
            ks = CompanyKeyshareholder(company_id=int(
                company_id), keyshareholders_name=key, description=desp, updated_by_id=request.user.id, pdf_id=key_share_holder_pdf_page.id)
            ks.save()

    for nominee, desp in zip(director_nominee, director_nominee_description):
        if nominee not in (None, ''):
            n = CompanyRepresentative(company_id=int(company_id), representative_name=nominee,
                                      description=desp, designation='Director Nominee', updated_by_id=request.user.id)
            n.save()

    for ceo_name, desp in zip(ceo, ceo_description):
        if ceo_name not in (None, ''):
            c = CompanyRepresentative(company_id=int(company_id), representative_name=ceo_name,
                                      description=desp, designation='CEO', updated_by_id=request.user.id, pdf_id=ceo_pdf_page.id)
            c.save()

    for cfo_name, desp in zip(cfo, cfo_description):
        if cfo_name not in (None, ''):
            cf = CompanyRepresentative(company_id=int(company_id), representative_name=cfo_name,
                                       description=desp, designation='CFO', updated_by_id=request.user.id)
            cf.save()

    for m, desp in zip(chair_dir, chair_dir_description):
        if m not in (None, ''):
            cd = CompanyRepresentative(company_id=int(company_id), representative_name=m,
                                       description=desp, designation='Chair. of B. Direc', updated_by_id=request.user.id)
            cd.save()

    for director, desp in zip(directors, directors_description):
        if director not in (None, ''):
            d = CompanyRepresentative(company_id=int(company_id), representative_name=director,
                                      description=desp, designation='Director', updated_by_id=request.user.id)
            d.save()

    return render(request, 'companymaster/addcompany_2.html', {'name': request.user.username, 'company_id': company_id})


@csrf_exempt
def offering_details_submit_form(request):
    """
    Store company offering related information announcement dates and status in database.
    Parameters:
        request: http POST request
    """

    post_data = json.loads(request.body)
    post_data = {k: None if not v else v for k, v in post_data.items()}
    for k, v in post_data.items():
        if not v:
            post_data[k] = None
        if k in ('listing_status', 'ipo_status', 'offer_status', 'type_of_listing'):
            if v is not None:
                post_data[k] = int(v)

    listing_status = post_data['listing_status']
    ipo_status = post_data['ipo_status']
    offer_status = post_data['offer_status']
    use_of_Proceeds = post_data['use_of_Proceeds']
    type_of_listing = post_data['type_of_listing']

    use_of_Proceeds_pdf = post_data['use_of_Proceeds_pdf']
    use_of_Proceeds_page_no = post_data['use_of_Proceeds_page_no']
    pdf = PDFModel.objects.filter(path=use_of_Proceeds_pdf).first()
    use_of_Proceeds_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=use_of_Proceeds_page_no)
    use_of_Proceeds_pdf_page.save()

    ipo_announcement_dt_pdf = post_data['ipo_announcement_dt_pdf']
    ipo_announcement_dt_page_no = post_data['ipo_announcement_dt_page_no']
    pdf = PDFModel.objects.filter(path=ipo_announcement_dt_pdf).first()
    ipo_announcement_dt_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=ipo_announcement_dt_page_no)
    ipo_announcement_dt_pdf_page.save()

    ipo_pr_announcement_dt_pdf = post_data['ipo_pr_announcement_dt_pdf']
    ipo_pr_announcement_dt_page_no = post_data['ipo_pr_announcement_dt_page_no']
    pdf = PDFModel.objects.filter(path=ipo_pr_announcement_dt_pdf).first()
    ipo_pr_announcement_dt_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=ipo_pr_announcement_dt_page_no)
    ipo_pr_announcement_dt_pdf_page.save()

    ipo_start_dt_pdf = post_data['ipo_start_dt_pdf']
    ipo_start_dt_page_no = post_data['ipo_start_dt_page_no']
    pdf = PDFModel.objects.filter(path=ipo_start_dt_pdf).first()
    ipo_start_dt_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=ipo_start_dt_page_no)
    ipo_start_dt_pdf_page.save()

    ipo_end_dt_pdf = post_data['ipo_end_dt_pdf']
    ipo_end_dt_page_no = post_data['ipo_end_dt_page_no']
    pdf = PDFModel.objects.filter(path=ipo_end_dt_pdf).first()
    ipo_end_dt_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=ipo_end_dt_page_no)
    ipo_end_dt_pdf_page.save()

    share_issue_dt_pdf = post_data['share_issue_dt_pdf']
    share_issue_dt_page_no = post_data['share_issue_dt_page_no']
    pdf = PDFModel.objects.filter(path=share_issue_dt_pdf).first()
    share_issue_dt_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=share_issue_dt_page_no)
    share_issue_dt_pdf_page.save()

    date_of_listing_pdf = post_data['date_of_listing_pdf']
    date_of_listing_page_no = post_data['date_of_listing_page_no']
    pdf = PDFModel.objects.filter(path=date_of_listing_pdf).first()
    date_of_listing_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=date_of_listing_page_no)
    date_of_listing_pdf_page.save()

    postpone_date_pdf = post_data['postpone_date_pdf']
    postpone_date_page_no = post_data['postpone_date_page_no']
    pdf = PDFModel.objects.filter(path=postpone_date_pdf).first()
    postpone_date_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=postpone_date_page_no)
    postpone_date_pdf_page.save()

    withdrawn_date_pdf = post_data['withdrawn_date_pdf']
    withdrawn_date_page_no = post_data['withdrawn_date_page_no']
    pdf = PDFModel.objects.filter(path=withdrawn_date_pdf).first()
    withdrawn_date_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=withdrawn_date_page_no)
    withdrawn_date_pdf_page.save()

    ipo_announcement_dt = post_data['ipo_announcement_dt']
    if ipo_announcement_dt is not None:
        ipo_announcement_dt = datetime.datetime.strptime(
            ipo_announcement_dt, '%m/%d/%Y').strftime('%Y-%m-%d')

    ipo_pr_announcement_dt = post_data['ipo_pr_announcement_dt']
    if ipo_pr_announcement_dt is not None:
        ipo_pr_announcement_dt = datetime.datetime.strptime(
            ipo_pr_announcement_dt, '%m/%d/%Y').strftime('%Y-%m-%d')

    ipo_start_dt = post_data['ipo_start_dt']
    if ipo_start_dt is not None:
        ipo_start_dt = datetime.datetime.strptime(
            ipo_start_dt, '%m/%d/%Y').strftime('%Y-%m-%d')

    ipo_end_dt = post_data['ipo_end_dt']
    if ipo_end_dt is not None:
        ipo_end_dt = datetime.datetime.strptime(
            ipo_end_dt, '%m/%d/%Y').strftime('%Y-%m-%d')

    share_issue_dt = post_data['share_issue_dt']
    if share_issue_dt is not None:
        share_issue_dt = datetime.datetime.strptime(
            share_issue_dt, '%m/%d/%Y').strftime('%Y-%m-%d')

    date_of_listing = post_data['date_of_listing']
    if date_of_listing is not None:
        date_of_listing = datetime.datetime.strptime(
            date_of_listing, '%m/%d/%Y').strftime('%Y-%m-%d')

    snapshot_date = post_data['snapshot_date']
    if snapshot_date is not None:
        snapshot_date = datetime.datetime.strptime(
            snapshot_date, '%m/%d/%Y').strftime('%Y-%m-%d')

    withdrawn_date = post_data['withdrawn_date']
    if withdrawn_date is not None:
        withdrawn_date = datetime.datetime.strptime(
            withdrawn_date, '%m/%d/%Y').strftime('%Y-%m-%d')

    postpone_date = post_data['postpone_date']
    if postpone_date is not None:
        postpone_date = datetime.datetime.strptime(
            postpone_date, '%m/%d/%Y').strftime('%Y-%m-%d')

    offering_id = int(post_data['choice'])
    company_id = int(post_data['company'][0])

    # if post_data has 'tid' (which is company offering mapping id), it indicates that the record is present in Offering transaction table and there is no need to make new entry (update form).
    # if 'tid' is not present in post_data it means need to make new entry (add form).
    if 'tid' not in post_data.keys():
        offering_info = Offering(
            offering_id=offering_id, company_id=company_id, updated_by_id=request.user.id)
        offering_info.save()
        company_offering_id = offering_info.id
    else:
        company_offering_id = post_data['tid']

    offering_status_info = CompanyOfferingStatus(withdrawn_date_pdf_id=withdrawn_date_pdf_page.id, postpone_date_pdf_id=postpone_date_pdf_page.id, date_of_listing_pdf_id=date_of_listing_pdf_page.id, share_issue_date_pdf_id=share_issue_dt_pdf_page.id, offering_end_date_pdf_id=ipo_end_dt_pdf_page.id, offering_start_date_pdf_id=ipo_start_dt_pdf_page.id, offering_price_announcement_date_pdf_id=ipo_pr_announcement_dt_pdf_page.id, offering_announcement_date_pdf_id=ipo_announcement_dt_pdf_page.id, use_of_proceeds_pdf_id=use_of_Proceeds_pdf_page.id, snapshot_date=snapshot_date, date_of_listing=date_of_listing, share_issue_date=share_issue_dt, offering_end_date=ipo_end_dt, offering_start_date=ipo_start_dt, postpone_date=postpone_date, withdrawn_date=withdrawn_date, offering_price_announcement_date=ipo_pr_announcement_dt,
                                                 offering_announcement_date=ipo_announcement_dt, type_of_listing_id=type_of_listing, offer_status_id=offer_status, listing_status_id=listing_status, IPO_status_id=ipo_status, use_of_proceeds=use_of_Proceeds, company_offering_id=company_offering_id, updated_by_id=request.user.id)
    offering_status_info.save()

    return render(request, 'companymaster/addcompany_3.html', {'name': request.user.username, 'company_offering_id': company_offering_id})


@csrf_exempt
def offering_shares_submit_form(request):
    """
    Store company offering shares related information in database.
    Parameters:
        request: http POST request
    """
    # get post data
    post_data = json.loads(request.body)
    post_data = {k: None if not v else v for k, v in post_data.items()}
    for k, v in post_data.items():
        try:
            if v is not None:
                post_data[k] = Decimal(v)
        except:
            pass
    shares_offered_min = post_data['shares_offered_min']
    shares_offered_max = post_data['shares_offered_max']
    strategic_shares_off = post_data['strategic_shares_off']
    add_sh_off_above_ipo = post_data['add_sh_off_above_ipo']
    offer_amount_min = post_data['offer_amount_min']
    offer_amount_max = post_data['offer_amount_max']
    price_range_min = post_data['price_range_min']
    price_range_max = post_data['price_range_max']
    no_of_shares_issued = post_data['no_of_shares_issued']
    shares_after_str = post_data['shares_after_str']
    underwriting_discount = post_data['underwriting_discount']
    proceeds_after_expense = post_data['proceeds_after_expense']
    sh_shares_offered = post_data['sh_shares_offered']
    shares_outstanding = post_data['shares_outstanding']
    registration_fee = post_data['registration_fee']
    typ_of_eq_instrument = post_data['typ_of_eq_instrument']
    security_description = post_data['security_description']
    warants_issued = post_data['warants_issued']
    lockup_period = post_data['lockup_period']
    ex_price_of_warants = post_data['ex_price_of_warants']

    shares_offered_min_pdf = post_data['shares_offered_min_pdf']
    shares_offered_min_page_no = post_data['shares_offered_min_page_no']
    pdf = PDFModel.objects.filter(path=shares_offered_min_pdf).first()
    shares_offered_min_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=shares_offered_min_page_no)
    shares_offered_min_pdf_page.save()

    offer_amount_min_pdf = post_data['offer_amount_min_pdf']
    offer_amount_min_page_no = post_data['offer_amount_min_page_no']
    pdf = PDFModel.objects.filter(path=offer_amount_min_pdf).first()
    offer_amount_min_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=offer_amount_min_page_no)
    offer_amount_min_pdf_page.save()

    price_range_min_pdf = post_data['price_range_min_pdf']
    price_range_min_page_no = post_data['price_range_min_page_no']
    pdf = PDFModel.objects.filter(path=price_range_min_pdf).first()
    price_range_min_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=price_range_min_page_no)
    price_range_min_pdf_page.save()

    registration_fee_pdf = post_data['registration_fee_pdf']
    registration_fee_page_no = post_data['registration_fee_page_no']
    pdf = PDFModel.objects.filter(path=registration_fee_pdf).first()
    registration_fee_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=registration_fee_page_no)
    registration_fee_pdf_page.save()

    lockup_period_pdf = post_data['lockup_period_pdf']
    lockup_period_page_no = post_data['lockup_period_page_no']
    pdf = PDFModel.objects.filter(path=lockup_period_pdf).first()
    lockup_period_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=lockup_period_page_no)
    lockup_period_pdf_page.save()

    quiet_period_expiration_pdf = post_data['quiet_period_expiration_pdf']
    quiet_period_expiration_page_no = post_data['quiet_period_expiration_page_no']
    pdf = PDFModel.objects.filter(path=quiet_period_expiration_pdf).first()
    quiet_period_expiration_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=quiet_period_expiration_page_no)
    quiet_period_expiration_pdf_page.save()

    total_offering_exp_pdf = post_data['total_offering_exp_pdf']
    total_offering_exp_page_no = post_data['total_offering_exp_page_no']
    pdf = PDFModel.objects.filter(path=total_offering_exp_pdf).first()
    total_offering_exp_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=total_offering_exp_page_no)
    total_offering_exp_pdf_page.save()

    lockup_expiration = post_data['lockup_expiration']
    if lockup_expiration is not None:
        lockup_expiration = datetime.datetime.strptime(
            lockup_expiration, '%m/%d/%Y').strftime('%Y-%m-%d')

    quiet_period_expiration = post_data['quiet_period_expiration']
    if quiet_period_expiration is not None:
        quiet_period_expiration = datetime.datetime.strptime(
            quiet_period_expiration, '%m/%d/%Y').strftime('%Y-%m-%d')

    greenshoe_opt_exercise_dt = post_data['greenshoe_opt_exercise_dt']
    if greenshoe_opt_exercise_dt is not None:
        greenshoe_opt_exercise_dt = datetime.datetime.strptime(
            greenshoe_opt_exercise_dt, '%m/%d/%Y').strftime('%Y-%m-%d')

    no_of_grreenshoe_sh_iss = post_data['no_of_grreenshoe_sh_iss']
    shares_overalloted = post_data['shares_overalloted']
    total_offering_exp = post_data['total_offering_exp']
    legal_fees_exp = post_data['legal_fees_exp']
    security_parvalue = post_data['security_parvalue']
    security_parvalue_curr = post_data['security_parvalue_curr']
    prospectus_link = post_data['prospectus_link']

    snapshot_date = post_data['snapshot_date']
    if snapshot_date is not None:
        snapshot_date = datetime.datetime.strptime(
            snapshot_date, '%m/%d/%Y').strftime('%Y-%m-%d')

    offering_id = post_data['offering']
    company_id = int(post_data['company'][0])
    # if post_data has 'tid' (which is company offering mapping id) then update record with company_offering_id=tid (update form).
    # if 'tid' is not present in post_data it means need to make new entry by taking company_id and offering_id from Offering table for current user (add form)
    if 'tid' not in post_data.keys():
        company_offering = Offering.objects.filter(
            company_id=company_id, offering_id=offering_id, updated_by=request.user.id).last()
        company_offering_id = company_offering.id
    else:
        company_offering_id = post_data['tid']

    # insert company offering shares related information
    offering_share_info = CompanyOfferingShares(total_offering_exp_pdf_id=total_offering_exp_pdf_page.id, quiet_period_expiration_pdf_id=quiet_period_expiration_pdf_page.id, lockup_period_pdf_id=lockup_period_pdf_page.id, registration_fee_pdf_id=registration_fee_pdf_page.id, price_range_min_pdf_id=price_range_min_pdf_page.id, offer_amount_min_pdf_id=offer_amount_min_pdf_page.id, shares_offered_min_pdf_id=shares_offered_min_pdf_page.id, number_of_greenshoe_shares_issued=no_of_grreenshoe_sh_iss, greenshoe_option_exercise_date=greenshoe_opt_exercise_dt, shares_overalloted=shares_overalloted, number_of_shares_issued=no_of_shares_issued, quiet_period_expiration_date=quiet_period_expiration, lockup_expiration_date=lockup_expiration, lockup_period=lockup_period, shares_outstanding=shares_outstanding, shareholder_shares_offered=sh_shares_offered, proceeds_after_expense=proceeds_after_expense, underwriting_discount=underwriting_discount,
                                                price_range_max=price_range_max, price_range_min=price_range_min, offer_amount_max=offer_amount_max, offer_amount_min=offer_amount_min, additional_shares_offered_aboveIPO=add_sh_off_above_ipo, strategic_shares_offered=strategic_shares_off, shares_offered_max=shares_offered_max, shares_offered_min=shares_offered_min, snapshot_date=snapshot_date, strategic_sale_offer_that_were_issued=shares_after_str, prospectus_link=prospectus_link, company_offering_id=company_offering_id, updated_by=request.user)
    offering_share_info.save()

    # insert company offering fees related information
    offering_share_expense_info = CompanyOfferingFeesExpense(security_parvalue=security_parvalue, legal_fees_expenses=legal_fees_exp, total_offering_expense=total_offering_exp, warants_issued=warants_issued, security_description=security_description,
                                                             type_of_equity_instrument=typ_of_eq_instrument, registeration_fee=registration_fee, currency_id=security_parvalue_curr, ex_price_of_warants=ex_price_of_warants, snapshot_date=snapshot_date, company_offering_id=company_offering_id, updated_by=request.user)
    offering_share_expense_info.save()

    return render(request, 'companymaster/addcompany_4.html', {'name': request.user.username, 'company_offering_id': company_offering_id})


@csrf_exempt
def financial_submit_form(request):
    """
    Store company offering financials related information in database.
    Parameters:
        request: http POST request
    """
    post_data = json.loads(request.body)
    post_data = {k: None if not v else v for k, v in post_data.items()}
    from decimal import Decimal
    for k, v in post_data.items():
        try:
            if v is not None:
                post_data[k] = Decimal(v)
        except:
            pass
    snapshot_date = post_data['date']
    if snapshot_date is not None:
        snapshot_date = datetime.datetime.strptime(
            snapshot_date, '%m/%d/%Y').strftime('%Y-%m-%d')

    revenue = post_data['revenue']
    net_income = post_data['net_income']
    ebit = post_data['ebit']
    ebidta = post_data['ebidta']
    y_o_y_growth = post_data['y_o_y_growth']
    last_12_month_sales = post_data['last_12_month_sales']
    last_24_month_sales = post_data['last_24_month_sales']
    total_assets = post_data['total_assets']
    total_liabilities = post_data['total_liabilities']
    cash = post_data['cash']
    debt = post_data['debt']
    equity = post_data['equity']
    offering_id = post_data['offering']
    company_id = int(post_data['company'][0])

    revenue_pdf = post_data['revenue_pdf']
    revenue_page_no = post_data['revenue_page_no']
    pdf = PDFModel.objects.filter(path=revenue_pdf).first()
    revenue_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=revenue_page_no)
    revenue_pdf_page.save()

    last_12_month_sales_pdf = post_data['last_12_month_sales_pdf']
    print(last_12_month_sales_pdf)
    last_12_month_sales_page_no = post_data['last_12_month_sales_page_no']
    pdf = PDFModel.objects.filter(path=last_12_month_sales_pdf).first()
    last_12_month_sales_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=last_12_month_sales_page_no)
    last_12_month_sales_pdf_page.save()

    total_assets_pdf = post_data['total_assets_pdf']
    total_assets_page_no = post_data['total_assets_page_no']
    pdf = PDFModel.objects.filter(path=total_assets_pdf).first()
    total_assets_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=total_assets_page_no)
    total_assets_pdf_page.save()

    cash_pdf = post_data['cash_pdf']
    cash_page_no = post_data['cash_page_no']
    pdf = PDFModel.objects.filter(path=cash_pdf).first()
    cash_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=cash_page_no)
    cash_pdf_page.save()

    debt_pdf = post_data['debt_pdf']
    debt_page_no = post_data['debt_page_no']
    pdf = PDFModel.objects.filter(path=debt_pdf).first()
    debt_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=debt_page_no)
    debt_pdf_page.save()

    equity_pdf = post_data['equity_pdf']
    equity_page_no = post_data['equity_page_no']
    pdf = PDFModel.objects.filter(path=equity_pdf).first()
    equity_pdf_page = PDFPage(
        pdf_id=pdf.id, page_no=equity_page_no)
    equity_pdf_page.save()

    # if post_data has 'tid' (which is company offering mapping id) then update record with company_offering_id=tid (update form).
    # if 'tid' is not present in post_data it means need to make new entry by taking company_id and offering_id from Offering table for current user (add form)
    if 'tid' not in post_data.keys():
        company_offering = Offering.objects.filter(
            company_id=company_id, offering_id=offering_id, updated_by=request.user.id).last()
        company_offering_id = company_offering.id
    else:
        company_offering_id = post_data['tid']

    financial_info = CompanyFinancial(equity_pdf_id=equity_pdf_page.id, debt_pdf_id=debt_pdf_page.id, cash_pdf_id=cash_pdf_page.id, total_assets_pdf_id=total_assets_pdf_page.id, last_12_month_sales_pdf_id=last_12_month_sales_pdf_page.id, revenue_pdf_id=revenue_pdf_page.id, equity=equity, debt=debt, cash=cash, total_liabilities=total_liabilities, last_24_months_sales=last_24_month_sales, last_12_months_sales=last_12_month_sales, y_o_y_growth=y_o_y_growth,
                                      ebitda=ebidta, ebit=ebit, net_income=net_income, revenue=revenue, snapshot_date=snapshot_date, total_assets=total_assets, company_offering_id=company_offering_id, updated_by=request.user)
    financial_info.save()
    return render(request, 'companymaster/addcompany_5.html', {'name': request.user.username})