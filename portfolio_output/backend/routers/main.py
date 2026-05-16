from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models import *

router = APIRouter(prefix='/p_r_prince_rehman_manjee,_ee,_mis_portfolio', tags=['p_r_prince_rehman_manjee,_ee,_mis_portfolio'])

@router.get('/profile_views', response_model=List[Profile_view])
async def list_profile_views():
    # Logic to fetch from satellite instance
    return []

@router.post('/profile_views', response_model=Profile_view)
async def create_profile_views(item: Profile_viewCreate):
    # Logic to insert into satellite instance
    return item

@router.get('/profile_views/{id}', response_model=Profile_view)
async def get_profile_views(id: str):
    # Logic to fetch single record
    return {}

@router.get('/contact_messages', response_model=List[Contact_message])
async def list_contact_messages():
    # Logic to fetch from satellite instance
    return []

@router.post('/contact_messages', response_model=Contact_message)
async def create_contact_messages(item: Contact_messageCreate):
    # Logic to insert into satellite instance
    return item

@router.get('/contact_messages/{id}', response_model=Contact_message)
async def get_contact_messages(id: str):
    # Logic to fetch single record
    return {}

