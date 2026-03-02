import * as React from "react";

// テーブルコンポーネント
export const Table = React.forwardRef<
  HTMLTableElement,
  React.HTMLAttributes<HTMLTableElement>
>(({ className, ...props }, ref) => (
  <table
    ref={ref}
    className={`w-full caption-bottom text-sm ${className || ""}`}
    {...props}
  />
));
Table.displayName = "Table";

// テーブルヘッダーコンポーネント
export const TableHeader = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <thead ref={ref} className={`[&_tr]:border-b ${className || ""}`} {...props} />
));
TableHeader.displayName = "TableHeader";

// テーブルボディコンポーネント
export const TableBody = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tbody
    ref={ref}
    className={`[&_tr:last-child]:border-0 ${className || ""}`}
    {...props}
  />
));
TableBody.displayName = "TableBody";

// テーブルフッターコンポーネント
export const TableFooter = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tfoot
    ref={ref}
    className={`bg-primary font-medium text-primary-foreground ${className || ""}`}
    {...props}
  />
));
TableFooter.displayName = "TableFooter";

// テーブル行コンポーネント
export const TableRow = React.forwardRef<
  HTMLTableRowElement,
  React.HTMLAttributes<HTMLTableRowElement>
>(({ className, ...props }, ref) => (
  <tr
    ref={ref}
    className={`border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted ${className || ""}`}
    {...props}
  />
));
TableRow.displayName = "TableRow";

// テーブルヘッドコンポーネント
export const TableHead = React.forwardRef<
  HTMLTableCellElement,
  React.ThHTMLAttributes<HTMLTableCellElement>
>(({ className, ...props }, ref) => (
  <th
    ref={ref}
    className={`h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0 ${className || ""}`}
    {...props}
  />
));
TableHead.displayName = "TableHead";

// テーブルセルコンポーネント
export const TableCell = React.forwardRef<
  HTMLTableCellElement,
  React.TdHTMLAttributes<HTMLTableCellElement>
>(({ className, ...props }, ref) => (
  <td
    ref={ref}
    className={`p-4 align-middle [&:has([role=checkbox])]:pr-0 ${className || ""}`}
    {...props}
  />
));
TableCell.displayName = "TableCell";

// テーブルキャプションコンポーネント
export const TableCaption = React.forwardRef<
  HTMLTableCaptionElement,
  React.HTMLAttributes<HTMLTableCaptionElement>
>(({ className, ...props }, ref) => (
  <caption
    ref={ref}
    className={`mt-4 text-sm text-muted-foreground ${className || ""}`}
    {...props}
  />
));
TableCaption.displayName = "TableCaption";
