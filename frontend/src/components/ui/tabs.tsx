import * as React from "react";

// タブコンテキスト
const TabsContext = React.createContext<{
  value: string;
  onValueChange: (value: string) => void;
}>({
  value: "",
  onValueChange: () => {},
});

// タブコンポーネント
export const Tabs = ({ 
  defaultValue, 
  children,
  ...props 
}: { 
  defaultValue: string;
  children: React.ReactNode;
} & React.HTMLAttributes<HTMLDivElement>) => {
  const [value, setValue] = React.useState(defaultValue);
  
  return (
    <TabsContext.Provider value={{ value, onValueChange: setValue }}>
      <div {...props}>
        {children}
      </div>
    </TabsContext.Provider>
  );
};

// タブリストコンポーネント
export const TabsList = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={`inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground ${className || ""}`} {...props} />
);

// タブトリガーコンポーネント
export const TabsTrigger = ({ 
  className, 
  value,
  ...props 
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { 
  value: string;
}) => {
  const { value: selectedValue, onValueChange } = React.useContext(TabsContext);
  const isActive = selectedValue === value;
  
  return (
    <button
      className={`inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm ${className || ""}`}
      onClick={() => onValueChange(value)}
      data-state={isActive ? "active" : "inactive"}
      {...props}
    />
  );
};

// タブコンテンツコンポーネント
export const TabsContent = ({ 
  className, 
  value,
  ...props 
}: React.HTMLAttributes<HTMLDivElement> & { 
  value: string;
}) => {
  const { value: selectedValue } = React.useContext(TabsContext);
  const isActive = selectedValue === value;
  
  if (!isActive) return null;
  
  return (
    <div
      className={`mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${className || ""}`}
      data-state={isActive ? "active" : "inactive"}
      {...props}
    />
  );
}; 