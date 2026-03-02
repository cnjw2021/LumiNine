'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { NineStarDataTable } from './NineStarDataTable';
import { SolarStartsDataTable } from './SolarStartsDataTable';
import { SolarTermsDataTable } from './SolarTermsDataTable';

export default function DataManagementPage() {
  return (
    <div className="container mx-auto py-10">
      <Card className="shadow-lg">
        <CardHeader className="bg-gray-50">
          <CardTitle>データ管理</CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="w-full">
            <Tabs defaultValue="nine-star" className="w-full">
              <TabsList className="grid w-full grid-cols-3 mb-6">
                <TabsTrigger value="nine-star">九星データ</TabsTrigger>
                <TabsTrigger value="solar-starts">立春データ</TabsTrigger>
                <TabsTrigger value="solar-terms">二十四節気データ</TabsTrigger>
              </TabsList>
              
              <TabsContent value="nine-star" className="mt-0">
                <NineStarDataTable />
              </TabsContent>
              <TabsContent value="solar-starts" className="mt-0">
                <SolarStartsDataTable />
              </TabsContent>
              <TabsContent value="solar-terms" className="mt-0">
                <SolarTermsDataTable />
              </TabsContent>
            </Tabs>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
