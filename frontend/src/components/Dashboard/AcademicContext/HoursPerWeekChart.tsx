import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { DashboardData } from '@/types/dashboard';
import { Box, Typography } from '@mui/material';

interface HoursPerWeekChartProps {
  data: DashboardData[];
  dataKey: string;
  title: string;
}

export const HoursPerWeekChart = ({ data, dataKey, title }: HoursPerWeekChartProps) => {
  data.sort((a, b) => (a[dataKey as keyof DashboardData] as number) - (b[dataKey as keyof DashboardData] as number));
  const groupedData = data.reduce((acc, curr) => {
    // Filter out null values
    if (curr[dataKey as keyof DashboardData] === 0) {
      return acc;
    }
    const group = acc.find(item => item.hours === curr[dataKey as keyof DashboardData]);
    if (group) {
      group[curr.predictions === 1 ? 'prediction_1' : 'prediction_0'] += 1;
    } else {
      acc.push({
        hours: curr[dataKey as keyof DashboardData] as number,
        prediction_0: curr.predictions === 0 ? 1 : 0,
        prediction_1: curr.predictions === 1 ? 1 : 0,
      });
    }
    return acc;
  }, [] as { hours: number; prediction_0: number; prediction_1: number }[]);

  groupedData.unshift({hours: 0, prediction_0: 0, prediction_1: 0});

  return (
    <Box>
      <Typography variant="h6" align="center" gutterBottom>
        {title}
      </Typography>
    <ResponsiveContainer width="100%" height={320}>
    <AreaChart data={groupedData}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="hours" angle={60} height={50} dy={10} dx={5}  interval={3}                    
      label={{ value: 'Hours', position: 'Bottom', dy: 20 }}/>
        <YAxis 
            label={{ value: 'Nr. of Students', angle: -90, position: 'Center',dx: -20 }}
            interval={1}
            tickFormatter={(value) => value.toFixed(0)}
            tickCount={10}
        />
      <YAxis />
      <Tooltip />
      <Area type="monotone" dataKey="prediction_0" name="No MH Issues" stackId="1" stroke="#82ca9d" fill="#82ca9d" />
      <Area type="monotone" dataKey="prediction_1" name="MH Issues" stackId="1" stroke="#ff0000" fill="#ff0000" />
    </AreaChart>
    </ResponsiveContainer>
    </Box>
  );
};