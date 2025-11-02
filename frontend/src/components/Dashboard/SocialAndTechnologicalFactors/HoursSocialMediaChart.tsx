import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { DashboardData } from '@/types/dashboard';
import { Box, Typography } from '@mui/material';

interface HoursSocialMediaChartProps {
  data: DashboardData[];
}

export const HoursSocialMediaChart = ({ data }: HoursSocialMediaChartProps) => {
  // Filter and process data
  const groupedData = data
    .filter(item => item.hours_socialmedia > 0) // Remove zeros
    .reduce((acc, curr) => {
      // Round hours to nearest number
      const roundedHours = Math.round(curr.hours_socialmedia);
      
      const group = acc.find(item => item.hours_socialmedia === roundedHours);
      if (group) {
        group[curr.predictions === 1 ? 'prediction_1' : 'prediction_0'] += 1;
      } else {
        acc.push({
          hours_socialmedia: roundedHours,
          prediction_0: curr.predictions === 0 ? 1 : 0,
          prediction_1: curr.predictions === 1 ? 1 : 0,
        });
      }
      return acc;
    }, [] as { hours_socialmedia: number; prediction_0: number; prediction_1: number }[])
    .sort((a, b) => a.hours_socialmedia - b.hours_socialmedia); // Sort by hours

  groupedData.unshift({hours_socialmedia: 0, prediction_0: 0, prediction_1: 0});

  return (
    <Box>
      <Typography variant="h6" align="center" gutterBottom>
        Daily Social Media Usage (Hours)
      </Typography>
      <ResponsiveContainer width="100%" height={350}>
        <AreaChart data={groupedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="hours_socialmedia"
            label={{ value: 'Hours', position: 'Bottom', dy: 20 }}
            dy={10} height={50} interval={1}
          />
          <YAxis 
            label={{ value: 'Nr. of Students', angle: -90, position: 'Center',dx: -20 }}
            interval={1}
            tickFormatter={(value) => value.toFixed(0)}
            tickCount={20}
          />
          <Tooltip />
          <Area 
            type="monotone" 
            dataKey="prediction_0" 
            name="No Mental Health Issues" 
            stackId="1" 
            stroke="#82ca9d" 
            fill="#82ca9d" 
          />
          <Area 
            type="monotone" 
            dataKey="prediction_1" 
            name="Mental Health Issues" 
            stackId="1" 
            stroke="#ff0000" 
            fill="#ff0000" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </Box>
  );
};