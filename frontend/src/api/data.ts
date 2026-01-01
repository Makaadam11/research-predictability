import { QuestionarieData } from '@/types/QuestionaireTypes';
import { DashboardData } from '@/types/dashboard';
import axios from 'axios';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export const submitQuestionaire = async (data: QuestionarieData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/submit/${data.source.toLowerCase()}`, data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const loadCourses = async (university: string): Promise<string[]> => {
  try {
    const response = await fetch(`/api/courses/${university}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch courses: ${response.statusText}`);
    }
    const data = await response.json();
    return data.courses;
  } catch (error) {
    console.error('Error loading courses:', error);
    return [];
  }
};

export const loadDepartments = async (university: string): Promise<any> => {
  try {
    console.log(`Loading departments for university: ${university}`);
    
    if (university === 'All') {
      // For "All", use the special endpoint
      const response = await fetch(`/api/departments/All`);
      if (!response.ok) {
        console.error(`Failed to fetch all departments: ${response.statusText}`);
        throw new Error(`Failed to fetch all departments: ${response.statusText}`);
      }
      const data = await response.json();
      console.log('All departments data received:', data);
      return data;
    } else {
      // For specific universities
      const response = await fetch(`/api/departments/${university}`);
      if (!response.ok) {
        console.error(`Failed to fetch departments for ${university}: ${response.statusText}`);
        throw new Error(`Failed to fetch departments: ${response.statusText}`);
      }
      const data = await response.json();
      console.log(`Departments for ${university} received:`, data);
      return data;
    }
  } catch (error) {
    console.error('Error loading departments:', error);
    return { departments: {} };
  }
};

export async function getDashboardData(university: string = 'All'): Promise<any> {
  try {
    console.log(`Getting dashboard data for university: ${university}`);
    const response = await fetch(`/api/dashboard?university=${university}`);
    
    if (!response.ok) {
      const error = await response.text();
      console.error(`Error fetching dashboard data: ${error}`);
      throw new Error('Failed to fetch dashboard data');
    }
    
    const data = await response.json();
    console.log(`Dashboard data received for ${university}: ${data.data.length} records`);
    return data;
  } catch (error) {
    console.error('Error in getDashboardData:', error);
    throw error;
  }
}

export const generateReport = async (filteredData: DashboardData[], chartImages: { [key: string]: string }) => {
  try {
    if (!filteredData?.length) throw new Error('Invalid filtered data');
    // if (!chartImages || !Object.keys(chartImages).length) throw new Error('No chart images provided');

    // Clean and transform the data
    const cleanedData = filteredData.map(item => ({
      ...item,
      // Convert numeric fields and handle NaN/null
      age: Number(item.age) || 0,
      hours_per_week_university_work: Number(item.hours_per_week_university_work) || 0,
      work_hours_per_week: Number(item.work_hours_per_week) || 0,
      hours_socialising: Number(item.hours_socialising) || 0,
      hours_socialmedia: Number(item.hours_socialmedia) || 0,
      total_device_hours: Number(item.total_device_hours) || 0,
      cost_of_study: Number(item.cost_of_study) || 0,
      hours_per_week_lectures: Number(item.hours_per_week_lectures) || 0,
      hours_between_lectures: Number(item.hours_between_lectures) || 0,
      exercise_per_week: Number(item.exercise_per_week) || 0,
      predictions: isNaN(Number(item.predictions)) ? 0 : Number(item.predictions), // Ensure predictions field is a valid number
      captured_at: item.captured_at || new Date().toISOString(), // Ensure captured_at field is included
    }));

    // Process and validate chart images
    // const processedChartImages = Object.fromEntries(
    //   Object.entries(chartImages)
    //     .filter(([_, value]) => value?.startsWith('data:image/'))
    //     .map(([key, value]) => [key, value])
    // );

    const payload = {
      data: cleanedData,
      charts: {}
      // charts: processedChartImages
    };

    const response = await fetch(`/api/reports`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    const responseData = await response.json();
    
    if (!response.ok) {
      throw new Error(`Server error: ${responseData.detail || JSON.stringify(responseData)}`);
    }
    
    return responseData;
  } catch (error: any) {
    console.error('Error generating report:', error);
    throw new Error(`Failed to generate report: ${error.message}`);
  }
};

export const viewReport = async (timestamp: string): Promise<Blob> => {
  try {
    const response = await axios.get(`/api/reports/view/${timestamp}`, {
      responseType: 'blob', // Important to handle binary data
    });
    return response.data;
  } catch (error: any) {
    console.error('Error viewing report:', error);
    throw new Error(`Failed to view report: ${error.message}`);
  }
};

export const deleteReport = async (timestamp: string): Promise<void> => {
  try {
    await axios.delete(`/api/reports/delete/${timestamp}`);
  } catch (error  : any) {
    console.error('Error deleting report:', error);
    throw new Error(`Failed to delete report: ${error.message}`);
  }
};