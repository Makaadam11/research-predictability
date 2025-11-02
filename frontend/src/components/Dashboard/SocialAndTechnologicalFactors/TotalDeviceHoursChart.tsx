import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { DashboardData } from '@/types/dashboard';
import { Box, Typography } from '@mui/material';

interface TotalDeviceHoursChartProps {
  data: DashboardData[];
}

export const TotalDeviceHoursChart = ({ data }: TotalDeviceHoursChartProps) => {
  data.sort((a, b) => a.total_device_hours - b.total_device_hours);
  const groupedData = data.reduce((acc, curr) => {
    if (curr.total_device_hours === 0) return acc;
    const group = acc.find(item => item.total_device_hours === curr.total_device_hours);
    if (group) {
      group[curr.predictions === 1 ? 'prediction_1' : 'prediction_0'] += 1;
    } else {
      acc.push({
        total_device_hours: curr.total_device_hours,
        prediction_0: curr.predictions === 0 ? 1 : 0,
        prediction_1: curr.predictions === 1 ? 1 : 0,
      });
    }
    return acc;
  }, [] as { total_device_hours: number; prediction_0: number; prediction_1: number }[]);

  groupedData.unshift({total_device_hours: 0, prediction_0: 0, prediction_1: 0});
  return (
    <Box>
      <Typography variant="h6" align="center" gutterBottom>
        Total Device Hours
      </Typography>
    <ResponsiveContainer width="100%" height={350}>
      <AreaChart data={groupedData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="total_device_hours" dy={10} height={50} interval={1}
                    label={{ value: 'Hours', position: 'Bottom', dy: 20 }}/>
        <YAxis 
            label={{ value: 'Nr. of Students', angle: -90, position: 'Center',dx: -20 }}
            interval={1}
            tickFormatter={(value) => value.toFixed(0)}
            tickCount={20}
        />
        <Tooltip />
        <Area type="monotone" dataKey="prediction_0" name="No MH Issues" stackId="1" stroke="#82ca9d" fill="#82ca9d" />
        <Area type="monotone" dataKey="prediction_1" name="MH Issues" stackId="1" stroke="#ff0000" fill="#ff0000" />
      </AreaChart>
    </ResponsiveContainer>
    </Box>
  );
};