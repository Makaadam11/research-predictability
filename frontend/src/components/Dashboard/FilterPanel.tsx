import React, { useMemo, useState, useEffect, useRef, useCallback } from 'react';
import { Paper, Typography, FormControl, Select, MenuItem, InputLabel, Checkbox, ListItemText, Collapse, Box, Chip } from '@mui/material';
import type { DashboardData, FilterState } from '../../types/dashboard';
import { loadDepartments } from '../../api/data';
import { debounce } from 'lodash';

interface FilterPanelProps {
  filters: FilterState;
  onFilterChange: (key: keyof FilterState, value: string[]) => void;
  data: DashboardData[];
  onYearChange: (year: string) => void;
  onUniversityChange: (university: string) => void;
  selectedYear: string;
}

export const FilterPanel = ({ data, filters, onFilterChange, onYearChange, onUniversityChange, selectedYear }: FilterPanelProps) => {
  const [loading, setLoading] = useState<{[key: string]: boolean}>({});
  const [departments, setDepartments] = useState<{ [key: string]: { [key: string]: string[] } }>({});
  const [openSections, setOpenSections] = useState<{ [key: string]: boolean }>({});
  const [enhancedData, setEnhancedData] = useState<DashboardData[]>([]);
  const [universities, setUniversities] = useState<string[]>([]);
  const [yearRange, setYearRange] = useState<{ start: Date | null, end: Date | null }>({ start: null, end: null });
  const [dataLoaded, setDataLoaded] = useState<boolean>(false);
  const initializedRef = useRef(false);

  // Cache for filtered data to avoid recalculating
  const filteredDataCache = useRef<{
    university: DashboardData[];
    year: DashboardData[];
    department: DashboardData[];
  }>({
    university: [],
    year: [],
    department: []
  });
  
  const prevDepsRef = useRef<{ selectedUniversity: string | null, deptCount: number }>({ 
    selectedUniversity: null, 
    deptCount: 0 
  });
  
  // Store the initial university from login data
  const [initialUniversity] = useState<string>(() => {
    return localStorage.getItem('university') || 'All';
  });
  
  const [selectedUniversity, setSelectedUniversity] = useState<string>(initialUniversity);
  const [selectedDepartment, setSelectedDepartment] = useState<string[]>(() => {
    return initialUniversity !== 'All' && departments[initialUniversity]
      ? Object.keys(departments[initialUniversity])
      : [];
  });
  const [searchTerm, setSearchTerm] = useState<string>('');

  const debouncedFilterChange = useMemo(
    () => debounce((key: keyof FilterState, value: string[]) => {
      onFilterChange(key, value);
    }, 300),
    [onFilterChange]
  );
  
  useEffect(() => {
    if (initializedRef.current) return;
  
    const initializeUniversity = async () => {
      try {
        const userUniversity = localStorage.getItem('university');
        
        // If user has All access, load both universities
        if (userUniversity === 'All') {
          setUniversities(['All', 'UAL', 'SOL']);
        } else {
          // Otherwise only load their assigned university
          setUniversities([userUniversity].filter(Boolean) as string[]);
        }
        
        setSelectedUniversity(userUniversity || 'All');
        onUniversityChange(userUniversity || 'All');
        
        initializedRef.current = true;
      } catch (error) {
        console.error('Error initializing university:', error);
        initializedRef.current = true;
      }
    };
  
    initializeUniversity();
  }, []);

  const hasSpecificUniversity = (): boolean => {
    return initialUniversity !== 'All';
  };

  const handleUniversityChange = (newUniversity: string) => {
    setSelectedUniversity(newUniversity);
    
    onUniversityChange(newUniversity);
    
    setSelectedDepartment([]);
    onFilterChange('course_of_study', []);
  };
  
  // Update department selection when university changes
  useEffect(() => {
    if (selectedUniversity && departments[selectedUniversity]) {
      const currentDeptCount = Object.keys(departments[selectedUniversity]).length;
      if (
        prevDepsRef.current.selectedUniversity === selectedUniversity &&
        prevDepsRef.current.deptCount === currentDeptCount
      ) {
        return; // Skip if nothing has changed
      }
      
      const allDepartments = Object.keys(departments[selectedUniversity]);
      setSelectedDepartment(allDepartments);
      onFilterChange('course_of_study', allDepartments.flatMap(dept => departments[selectedUniversity]?.[dept] || []));
      
      prevDepsRef.current = {
        selectedUniversity,
        deptCount: currentDeptCount
      };
    }
  }, [selectedUniversity, departments]);
  
  // Fetch departments for the selected university
  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        if (!selectedUniversity) return;
        
        setLoading(prev => ({ ...prev, departments: true }));
        
        if (selectedUniversity !== 'All') {
          setDepartments(prev => ({ ...prev, [selectedUniversity]: {} }));
        }
        
        const response = await loadDepartments(selectedUniversity);
        
        if (response && response.departments) {
          setDepartments(prev => ({ ...prev, [selectedUniversity]: response.departments }));
          
          const allDepartments = Object.keys(response.departments);
          
          if (allDepartments.length > 0) {
            setSelectedDepartment(allDepartments);
            
            const allCourses = allDepartments.flatMap(dept => response.departments[dept] || []);
            onFilterChange('course_of_study', allCourses);
          } else {
            setSelectedDepartment([]);
            onFilterChange('course_of_study', []);
          }
        } else {
          setSelectedDepartment([]);
          onFilterChange('course_of_study', []);
        }
      } catch (error) {
        console.error('Error loading departments:', error);
        setSelectedDepartment([]);
        onFilterChange('course_of_study', []);
      } finally {
        setLoading(prev => ({ ...prev, departments: false }));
      }
    };
    
    if (selectedUniversity && (!departments[selectedUniversity] || Object.keys(departments[selectedUniversity]).length === 0)) {
      fetchDepartments();
    }
  }, [selectedUniversity]);
  
  // Map courses to departments
  useEffect(() => {
    if (selectedUniversity && departments[selectedUniversity]) {
      const departmentMapping: { [course: string]: string } = {};
      const departmentsData = departments[selectedUniversity];
      
      Object.entries(departmentsData).forEach(([department, courses]) => {
        if (Array.isArray(courses)) {
          courses.forEach(course => {
            departmentMapping[course.toLowerCase()] = department;
          });
        }
      });
      
      const newData = data.map(item => {
        const mappedDepartment = item.course_of_study ? 
          departmentMapping[item.course_of_study.toLowerCase()] || 'Unknown' :
          'Unknown';
        
        return {
          ...item,
          department: mappedDepartment
        };
      });
      
      setEnhancedData(newData);
      setDataLoaded(true);
    }
  }, [departments, selectedUniversity, data]);

  // Update year range when selected year changes
  useEffect(() => {
    if (selectedYear && /^\d{4}-\d{4}$/.test(selectedYear)) {
      const [startYear, endYear] = selectedYear.split('-').map(Number);
      const startDate = new Date(startYear, 8, 1); 
      const endDate = new Date(endYear, 7, 31);
      setYearRange({ start: startDate, end: endDate });
    } else if (selectedYear === 'All') {
      const earliestYear = 2021; // Set the earliest year to 2021
      const startDate = new Date(earliestYear, 0, 1); // January 1, 2021
      const currentYear = new Date().getFullYear();
      const endDate = new Date(currentYear, 6, 31); // July 31 of the current year
      setYearRange({ start: startDate, end: endDate });
      onYearChange('All');
    } else {
      setYearRange({ start: null, end: null });
    }
  }, [selectedYear]);

  const getCurrentAcademicYear = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;
    return month >= 9 ? `${year}-${year + 1}` : `${year - 1}-${year}`;
  };
  
  const getAcademicYearsList = (data: DashboardData[]) => {
    const earliestDate = Math.min(...data
      .map(item => new Date(item.captured_at).getFullYear())
      .filter(year => !isNaN(year)));
    
    const currentYear = parseInt(getCurrentAcademicYear().split('-')[0]);
    
    const yearsList = [];
    for (let year = earliestDate; year <= currentYear; year++) {
      yearsList.push(`${year}-${year + 1}`);
    }
    yearsList.push('All');

    return yearsList;
  };
  
  const getAcademicYear = (dateString: string | undefined) => {
    if (!dateString) {
      return null;
    }
  
    const [datePart] = dateString.split(" ");
    const [day, month, year] = datePart.split(".").map(Number);
  
    if (isNaN(day) || isNaN(month) || isNaN(year)) {
      return null;
    }
  
    return month >= 9 ? `${year}-${year + 1}` : `${year - 1}-${year}`;
  };

  // Memoized filtered data for performance
  const filteredData = useMemo(() => {
    // First filter by university
    const universityFilteredData = data.filter(item => 
      !selectedUniversity || selectedUniversity === 'All' || item.source === selectedUniversity
    );
    
    // Cache the university filtered data
    filteredDataCache.current.university = universityFilteredData;

    // Then filter by year
    const yearFilteredData = universityFilteredData.filter(item => {
      const academicYear = getAcademicYear(item.captured_at);
      return selectedYear === 'All' || !selectedYear || academicYear === selectedYear;
    });
    
    // Cache the year filtered data
    filteredDataCache.current.year = yearFilteredData;

    // Then filter by departments/courses
    const departmentFilteredData = yearFilteredData.filter(item => {
      if (!selectedDepartment.length) return true;
      return selectedDepartment.some(dept => 
        departments[selectedUniversity]?.[dept]?.includes(item.course_of_study)
      );
    });
    
    // Cache the department filtered data
    filteredDataCache.current.department = departmentFilteredData;
    
    return departmentFilteredData;
  }, [enhancedData, selectedUniversity, selectedYear, selectedDepartment, departments]);

  // Memoized unique values for performance
  const dashboardData = useMemo(() => {
    if (!dataLoaded) return {};
    
    const getUnique = (key: keyof DashboardData, filterFn = (x: any) => !!x): any[] => {
      const values = filteredData.map(item => item[key]).filter(filterFn);
      return [...new Set(values)];
    };
    
    const getNumericUnique = (key: keyof DashboardData, min = 0, max = 100): any[] => {
      const values = filteredData.map(item => item[key])
        .filter(value => value !== undefined && value !== null)
        .filter(value => Number(value) >= min && Number(value) <= max);
      return [...new Set(values)].sort((a, b) => Number(a) - Number(b));
    };
  
    return {
      ethnic_group: getUnique('ethnic_group', x => x && x !== 'Not Provided'),
      home_country: getUnique('home_country', x => x && x !== 'Not Provided'),
      age: getNumericUnique('age', 0, 100),
      gender: getUnique('gender', x => x && x !== 'Not Provided'),
      student_type_location: getUnique('student_type_location', x => x && x !== 'Not Provided'),
      student_type_time: getUnique('student_type_time', x => x && x !== 'Not Provided'),
      course_of_study: selectedDepartment.length > 0 
        ? selectedDepartment.flatMap(dept => departments[selectedUniversity]?.[dept] || []) 
        : getUnique('course_of_study'),
      hours_between_lectures: getNumericUnique('hours_between_lectures', 0, 24),
      hours_per_week_lectures: getNumericUnique('hours_per_week_lectures', 0, 100),
      hours_per_week_university_work: getNumericUnique('hours_per_week_university_work', 0, 100),
      level_of_study: getUnique('level_of_study', x => x && x !== 'Not Provided'),
      timetable_preference: getUnique('timetable_preference', x => x && x !== 'Not Provided'),
      timetable_reasons: getUnique('timetable_reasons', x => x && x !== 'Not Provided'),
      timetable_impact: getUnique('timetable_impact', x => x && x !== 'Not Provided'),
      financial_support: getUnique('financial_support', x => x && x !== 'Not Provided'),
      financial_problems: getUnique('financial_problems', x => x && x !== 'Not Provided'),
      family_earning_class: getUnique('family_earning_class', x => x && x !== 'Not Provided'),
      form_of_employment: getUnique('form_of_employment', x => x && x !== 'Not Provided'),
      work_hours_per_week: getNumericUnique('work_hours_per_week', 0, 168),
      cost_of_study: getNumericUnique('cost_of_study', 0, 100000),
      diet: getUnique('diet', x => x && x !== 'Not Provided'),
      well_hydrated: getUnique('well_hydrated', x => x && x !== 'Not Provided'),
      exercise_per_week: getNumericUnique('exercise_per_week', 0, 100),
      alcohol_consumption: getUnique('alcohol_consumption', x => x && x !== 'Not Provided'),
      personality_type: getUnique('personality_type', x => x && x !== 'Not Provided'),
      physical_activities: getUnique('physical_activities', x => x && x !== 'Not Provided'),
      mental_health_activities: getUnique('mental_health_activities', x => x && x !== 'Not Provided'),
      hours_socialmedia: getNumericUnique('hours_socialmedia', 0, 24),
      total_device_hours: getNumericUnique('total_device_hours', 0, 24),
      hours_socialising: getNumericUnique('hours_socialising', 0, 168),
      quality_of_life: getUnique('quality_of_life', x => x && x !== 'Not Provided'),
      feel_afraid: getUnique('feel_afraid', x => x && x !== 'Not Provided'),
      stress_in_general: getUnique('stress_in_general', x => x && x !== 'Not Provided'),
      stress_before_exams: getUnique('stress_before_exams', x => x && x !== 'Not Provided'),
      known_disabilities: getUnique('known_disabilities', x => x && x !== 'Not Provided'),
      sense_of_belonging: getUnique('sense_of_belonging', x => x && x !== 'Not Provided'),
      captured_at: getAcademicYearsList(filteredDataCache.current.university),
    };
  }, [filteredData, selectedUniversity, selectedDepartment, departments, dataLoaded]);

  // Optimized year counts calculation
  const getYearCounts = useCallback(() => {
    if (!dataLoaded) return {};
    
    const counts: { [key: string]: number } = {};
    
    // Use cached university filtered data
    const universityFilteredData = filteredDataCache.current.university;
    
    // Count records for each year
    universityFilteredData.forEach(item => {
      if (item.captured_at) {
        const academicYear = getAcademicYear(item.captured_at);
        if (academicYear) {
          counts[academicYear] = (counts[academicYear] || 0) + 1;
        }
      }
    });
    
    // Calculate 'All' count as sum of all year counts
    counts['All'] = Object.values(counts).reduce((sum, count) => sum + count, 0);
    
    return counts;
  }, [dataLoaded]);

  // Optimized department counts calculation
  const getDepartmentCounts = useCallback(() => {
    if (!dataLoaded || !selectedUniversity || !departments[selectedUniversity]) return {};
    
    const counts: { [key: string]: number } = {};
    
    // Use the enhanced data that has department mapping applied
    const relevantData = enhancedData.filter(item => {
      // Filter by university
      const matchesUniversity = !selectedUniversity || selectedUniversity === 'All' || item.source === selectedUniversity;
      
      // Filter by year
      const academicYear = getAcademicYear(item.captured_at);
      const matchesYear = selectedYear === 'All' || !selectedYear || academicYear === selectedYear;
      
      return matchesUniversity && matchesYear;
    });
    
    // Count records for each department
    relevantData.forEach(item => {
      if (item.department && item.department !== 'Unknown') {
        counts[item.department] = (counts[item.department] || 0) + 1;
      }
    });
  
    return counts;
  }, [dataLoaded, selectedUniversity, selectedYear, enhancedData, departments]);

  // Optimized university counts calculation
  const getUniversityCounts = useCallback(() => {
    if (!dataLoaded) return {};
    
    const counts: { [key: string]: number } = {};
    
    // Count records for each university
    data.forEach(item => {
      if (item.source) {
        counts[item.source] = (counts[item.source] || 0) + 1;
      }
    });
    
    // Calculate 'All' count as sum of all university counts
    counts['All'] = Object.values(counts).reduce((sum, count) => sum + count, 0);
    
    return counts;
  }, [data, dataLoaded]);
  
  const toggleSection = (section: string) => {
    setOpenSections(prev => ({ ...prev, [section]: !prev[section] }));
  };
  
  const handleDepartmentChange = (event: any) => {
    const value = event.target.value;
    const allDepartments = Object.keys(departments[selectedUniversity] || {});
    
    if (value.includes('all')) {
      if (selectedDepartment.length === allDepartments.length) {
        setSelectedDepartment([]);
        onFilterChange('course_of_study', []);
      } else {
        setSelectedDepartment(allDepartments);
        // When 'All' is selected, combine all courses from all departments
        const allCourses = allDepartments.flatMap(dept => departments[selectedUniversity]?.[dept] || []);
        onFilterChange('course_of_study', allCourses);
      }
    } else {
      if (value.length === 0) {
        setSelectedDepartment([]);
        onFilterChange('course_of_study', []);
      } else {
        setSelectedDepartment(value);
        // Combine courses from selected departments
        const selectedCourses = value.flatMap((dept: string) => departments[selectedUniversity]?.[dept] || []);
        onFilterChange('course_of_study', selectedCourses);
      }
    }
  };

  // Optimized filter count calculation
  const getFilteredDataCacheCount = useCallback((key: string, value: any = 'all'): number => {
    if (!dataLoaded) return 0;
    
    // Use cached filtered data for better performance
    const baseData = filteredDataCache.current.department;
    
    // For 'all' value, return the total count of the filtered data
    if (value === 'all') {
      return baseData.length;
    }
    
    // Count items where this specific field matches the value
    return baseData.filter(item => {
      const itemValue = item[key as keyof DashboardData];
      
      if (itemValue === null || itemValue === undefined) {
        return value === null || value === undefined;
      }
      
      return String(itemValue).toLowerCase() === String(value).toLowerCase();
    }).length;
  }, [dataLoaded]);

  const getFilteredDataDynamicCount = useCallback((key: string, value: any = 'all'): number => {
    const baseData = filteredData.filter(item => {
      return Object.entries(filters).every(([filterKey, filterValues]) => {
        if (filterKey === key) return true;
        if (!filterValues || filterValues.length === 0) return true;
        
        const itemValue = item[filterKey as keyof DashboardData];
        return filterValues.includes(String(itemValue));
      });
    });
  
    if (value === 'all') return baseData.length;
    
    // Policz ile rekordów ma konkretną wartość
    return baseData.filter(item => 
      String(item[key as keyof DashboardData]).toLowerCase() === String(value).toLowerCase()
    ).length;
  }, [filteredData, filters, dataLoaded]);

  // Optimized select rendering
  const renderSelect = (key: string, values: any[]) => {
    const handleChange = (event: any) => {
      const value = event.target.value as string[];
      setLoading(prev => ({ ...prev, [key]: true }));
      
      try {
        if (value.includes('all')) {
          if (filters[key as keyof FilterState]?.length === values.length) {
            debouncedFilterChange(key as keyof FilterState, []);
          } else {
            debouncedFilterChange(key as keyof FilterState, values);
          }
        } else if (value.length === 0) {
          debouncedFilterChange(key as keyof FilterState, []);
        } else {
          debouncedFilterChange(key as keyof FilterState, value);
        }
      } finally {
        setLoading(prev => ({ ...prev, [key]: false }));
      }
    };

    const getCount = (value: any = 'all') => {
      return key === 'course_of_study' 
        ? getFilteredDataCacheCount(key, value)
        : getFilteredDataDynamicCount(key, value);
    };


    const filteredValues = values.filter(value => getFilteredDataCacheCount(key, value) > 0)
      
    const searchFilteredValues = searchTerm 
      ? filteredValues.filter(value => 
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      : filteredValues;

    const currentSelected = filters[key as keyof FilterState] || [];

    const selectedOptionsCount = searchFilteredValues.filter(val => currentSelected.includes(val)).length;
    
    const totalOptionsCount = searchFilteredValues.length;

    return (
      <FormControl fullWidth sx={{ mt: 1, mb: 1 }}>
        <InputLabel>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</InputLabel>
        <Select
          multiple
          value={filters[key as keyof FilterState] || []}
          onChange={handleChange}
          renderValue={(selected) => (selected as string[]).join(', ')}
          MenuProps={{
            PaperProps: {
              style: {
                maxHeight: 48 * 4.5,
              },
            },
          }}
        >
          <MenuItem value="all">
            <Checkbox 
              checked={totalOptionsCount > 0 && selectedOptionsCount === totalOptionsCount}
              indeterminate={
              selectedOptionsCount > 0 && 
              selectedOptionsCount < totalOptionsCount
              }
            />
            <ListItemText primary={`Select All (${getCount()})`} />
          </MenuItem>
          
          {searchFilteredValues.map((value, index) => {
            const count = getCount(value);
            return (
              <MenuItem key={`${value}-${index}`} value={value}>
                <Checkbox 
                  checked={filters[key as keyof FilterState]?.includes(value)}
                  disabled={loading[key]}
                />
                <ListItemText
                  primary={`(${count}) ${value}`}
                />
              </MenuItem>
            );
          })}
          
          {searchTerm && searchFilteredValues.length === 0 && (
            <MenuItem disabled>
              <ListItemText primary="No courses match your search" />
            </MenuItem>
          )}
        </Select>
      </FormControl>
    );
  };

  return (
    <div>
      <Paper sx={{ p: 2, fontFamily: 'Georgia, serif' }}>
        <Typography variant="h5"  gutterBottom sx={{ textAlign: 'center', fontFamily: 'Georgia, serif' }}>
          Filters
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mb: 2, flexWrap: 'wrap' }}>
          <Chip 
            label={`Filtered Records: ${filteredData.length}`} 
            color="primary" 
            sx={{ fontFamily: 'Georgia, serif' }}
          />
        </Box>

        <FormControl fullWidth sx={{ mt: 1, mb: 1, minWidth: 200, maxWidth: '100%', fontFamily: 'Georgia, serif' }}>
            <InputLabel sx={{ fontFamily: 'Georgia, serif' }}>University</InputLabel>
            <Select
              value={selectedUniversity}
              onChange={(e) => handleUniversityChange(e.target.value)}
              disabled={hasSpecificUniversity()}
              sx={{ fontFamily: 'Georgia, serif' }}
            >
              {universities.map((university) => {
                const counts = getUniversityCounts();
                return (
                  <MenuItem key={university} value={university} sx={{ fontFamily: 'Georgia, serif' }}>
                    {university} ({counts[university] || 0})
                  </MenuItem>
                );
              })}
            </Select>
          </FormControl>
          
          <FormControl fullWidth sx={{ mt: 1, mb: 1, minWidth: 200, maxWidth: '100%', fontFamily: 'Georgia, serif' }}>
            <InputLabel sx={{ fontFamily: 'Georgia, serif' }}>Year</InputLabel>
            <Select
              value={selectedYear}
              onChange={(e) => {
                const newYear = e.target.value;
                onYearChange(newYear);
              }}
              sx={{ fontFamily: 'Georgia, serif' }}
            >
              {getAcademicYearsList(data).reverse().map((year) => {
                const yearCounts = getYearCounts();
                return (
                  <MenuItem key={year} value={year} sx={{ fontFamily: 'Georgia, serif' }}>
                    {year} ({yearCounts[year] || 0} records)
                  </MenuItem>
                );
              })}
            </Select>
          </FormControl>
          
          {selectedUniversity && (
            <Box style={{padding: 3}}>
              <Typography variant="h6" gutterBottom sx={{ textAlign: 'center', borderRadius: '5px', backgroundColor: '#ffff', fontFamily: 'Georgia, serif' }}>
                Departments
              </Typography>
              <FormControl fullWidth sx={{ mt: 1, mb: 1, minWidth: 200, maxWidth: '100%', fontFamily: 'Georgia, serif' }}>
                <InputLabel sx={{ fontFamily: 'Georgia, serif' }}>Department</InputLabel>
                  <Select
                    multiple
                    value={selectedDepartment}
                    onChange={handleDepartmentChange}
                    renderValue={(selected) => {
                      if (selected.length === Object.keys(departments[selectedUniversity] || {}).length) {
                        return "All";
                      }
                      return (selected as string[]).join(', ');
                    }}
                    sx={{ fontFamily: 'Georgia, serif' }}
                  >
                  <MenuItem value="all" sx={{ fontFamily: 'Georgia, serif' }}>
                    <Checkbox
                      checked={selectedDepartment.length === Object.keys(departments[selectedUniversity] || {}).length}
                      indeterminate={selectedDepartment.length > 0 && selectedDepartment.length < Object.keys(departments[selectedUniversity] || {}).length}
                    />
                    <ListItemText primary="All" sx={{ fontFamily: 'Georgia, serif' }} />
                  </MenuItem>
                  {Object.keys(departments[selectedUniversity] || {}).map((dept) => {
                    const counts = getDepartmentCounts();
                    if (counts[dept] === 0 || counts[dept] === undefined) return null;
                    return (
                      <MenuItem key={dept} value={dept} sx={{ fontFamily: 'Georgia, serif' }}>
                        <Checkbox checked={selectedDepartment.includes(dept)} />
                        <ListItemText primary={`(${counts[dept] || 0}) ${dept}`} sx={{ fontFamily: 'Georgia, serif' }} />
                      </MenuItem>
                    );
                  })}
                </Select>
              </FormControl>
            </Box>
          )}
          {selectedDepartment.length > 0 && (
            <Box style={{padding: 3}}>
              <Typography variant="h6" gutterBottom sx={{ textAlign: 'center', fontFamily: 'Georgia, serif'}}>
                Courses
              </Typography>

                <input
                  placeholder="Search courses..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onClick={(e) => e.stopPropagation()}
                  onKeyDown={(e) => e.stopPropagation()}
                  style={{ 
                    width: '100%', 
                    padding: '8px', 
                    border: '1px solid #ccc', 
                    borderRadius: '4px',
                    fontFamily: 'Georgia, serif',
                    marginBottom: "10px",
                  }}
                />
              
              {renderSelect('course_of_study', dashboardData?.course_of_study || []) }
            </Box>
          )}

        <hr />
        <Box onClick={() => toggleSection('demographics')} style={{cursor:'pointer', padding: 3}}>
          <Typography variant="h6" gutterBottom>
            Demographics
          </Typography>
        </Box>
        <Collapse in={openSections['demographics']} sx={{ minWidth: 200, maxWidth: '100%' }}>
          {
    
          renderSelect('ethnic_group', dashboardData.ethnic_group?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('home_country', dashboardData.home_country?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('age', dashboardData.age?.sort((a, b) => a - b) || [])}
          {renderSelect('gender', dashboardData.gender?.filter(value => value !== 'Not Provided') || [])}
        </Collapse>
        
        <hr />
        <Box onClick={() => toggleSection('academicContext')} style={{cursor:'pointer' , padding: 3}}>
          <Typography variant="h6" gutterBottom>
            Academic Context
          </Typography>
        </Box>
        <Collapse in={openSections['academicContext']} sx={{ width: '100%' }}>
          {renderSelect('hours_between_lectures', dashboardData.hours_between_lectures?.sort((a, b) => a - b) || [])}
          {renderSelect('hours_per_week_lectures', dashboardData.hours_per_week_lectures?.sort((a, b) => a - b) || [])}
          {renderSelect('hours_per_week_university_work', dashboardData.hours_per_week_university_work?.sort((a, b) => a - b) || [])}
          {renderSelect('level_of_study', dashboardData.level_of_study?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('timetable_preference', dashboardData.timetable_preference?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('timetable_reasons', dashboardData.timetable_reasons?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('timetable_impact', dashboardData.timetable_impact?.filter(value => value !== 'Not Provided') || [])}
        </Collapse>
        
        <hr />
        <Box onClick={() => toggleSection('socioeconomicFactors')} style={{cursor:'pointer' , padding: 3}}>
          <Typography variant="h6" gutterBottom>
            Socioeconomic Factors
          </Typography>
        </Box>
        <Collapse in={openSections['socioeconomicFactors']} sx={{ width: '100%' }}>
          {renderSelect('financial_support', dashboardData.financial_support?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('financial_problems', dashboardData.financial_problems?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('family_earning_class', dashboardData.family_earning_class?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('form_of_employment', dashboardData.form_of_employment?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('work_hours_per_week', dashboardData.work_hours_per_week?.sort((a, b) => a - b) || [])}
          {renderSelect('cost_of_study', dashboardData.cost_of_study?.sort((a, b) => a - b) || [])}
        </Collapse>
        
        <hr />
        <Box onClick={() => toggleSection('lifestyleAndBehaviour')} style={{cursor:'pointer', padding: 3}}>
          <Typography variant="h6" gutterBottom>
            Lifestyle and Behaviour
          </Typography>
        </Box>
        <Collapse in={openSections['lifestyleAndBehaviour']} sx={{ width: '100%' }}>
          {renderSelect('diet', dashboardData.diet?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('well_hydrated', dashboardData.well_hydrated?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('exercise_per_week', dashboardData.exercise_per_week?.sort((a, b) => a - b) || [])}
          {renderSelect('alcohol_consumption', dashboardData.alcohol_consumption?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('personality_type', dashboardData.personality_type?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('physical_activities', dashboardData.physical_activities?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('mental_health_activities', dashboardData.mental_health_activities?.filter(value => value !== 'Not Provided') || [])}
        </Collapse>
        
        <hr />
        <Box onClick={() => toggleSection('socialAndTechnologicalFactors')} style={{cursor:'pointer', padding: 3}}>
          <Typography variant="h6" gutterBottom>
            Social and Technological Factors
          </Typography>
        </Box>
        <Collapse in={openSections['socialAndTechnologicalFactors']} sx={{ width: '100%' }}>
          {renderSelect('hours_socialmedia', dashboardData.hours_socialmedia?.sort((a, b) => a - b)|| [])}
          {renderSelect('total_device_hours', dashboardData.total_device_hours?.sort((a, b) => a - b)|| [])}
          {renderSelect('hours_socialising', dashboardData.hours_socialising?.sort((a, b) => a - b)|| [])}
        </Collapse>
        
        <hr />
        <Box onClick={() => toggleSection('psychologicalAndEmotionalFactors')} style={{cursor:'pointer', padding: 3}}>
          <Typography variant="h6" gutterBottom>
            Psychological and Emotional Factors
          </Typography>
        </Box>
        <Collapse in={openSections['psychologicalAndEmotionalFactors']} sx={{ width: '100%' }}>
          {renderSelect('quality_of_life', dashboardData.quality_of_life?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('feel_afraid', dashboardData.feel_afraid?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('stress_in_general', dashboardData.stress_in_general || [])}
          {renderSelect('stress_before_exams', dashboardData.stress_before_exams?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('known_disabilities', dashboardData.known_disabilities?.filter(value => value !== 'Not Provided') || [])}
          {renderSelect('sense_of_belonging', dashboardData.sense_of_belonging?.filter(value => value !== 'Not Provided')|| [])}
        </Collapse>
      </Paper>
    </div>
  );
};