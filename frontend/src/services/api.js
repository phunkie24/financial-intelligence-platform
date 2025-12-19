import axios from 'axios'
import io from 'socket.io-client'

const API_URL = 'http://localhost:5000/api'
const SOCKET_URL = 'http://localhost:5000'

export const api = {
  getStats: async () => {
    const res = await axios.get(`${API_URL}/stats`)
    return res.data
  },

  searchCompanies: async (query) => {
    const res = await axios.get(`${API_URL}/search?q=${query}`)
    return res.data
  },

  getCompanyDetails: async (company) => {
    const res = await axios.get(`${API_URL}/company/${encodeURIComponent(company)}`)
    return res.data
  },

  getAlerts: async () => {
    const res = await axios.get(`${API_URL}/alerts`)
    return res.data
  }
}

export const socket = io(SOCKET_URL)
