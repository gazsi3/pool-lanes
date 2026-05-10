import { useState, useMemo } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";
import type { Final } from "../../types";
import { getSeedMap } from "../../analytics";

interface TableRow extends Final {
  winner: string;
  winnerLane: number;
  winnerNationality: string;
}

function buildRows(finals: Final[]): TableRow[] {
  return finals.map((f) => {
    const winner = f.entries.find((e) => e.position === 1);
    return {
      ...f,
      winner: winner?.name ?? "—",
      winnerLane: winner?.lane ?? 0,
      winnerNationality: winner?.nationality ?? "—",
    };
  });
}

function EntrySubRow({ final }: { final: Final }) {
  const seedMap = getSeedMap(final);
  const sorted = [...final.entries].sort((a, b) => (a.position ?? 99) - (b.position ?? 99));
  return (
    <div className="subrow">
      <table className="subrow-table">
        <thead>
          <tr>
            <th>Lane</th>
            <th>Athlete</th>
            <th>NAT</th>
            <th>Time</th>
            <th>Pos</th>
            <th>Seeded</th>
            <th>Diff</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((e) => {
            const seed = seedMap[e.lane];
            const diff = e.position !== null && seed !== undefined ? e.position - seed : null;
            return (
              <tr key={e.lane} className={e.position === 1 ? "subrow-winner" : ""}>
                <td>{e.lane}</td>
                <td>{e.name || "—"}</td>
                <td>{e.nationality}</td>
                <td>{e.final_time ?? (e.dsq ? "DSQ" : e.dns ? "DNS" : e.dnf ? "DNF" : "—")}</td>
                <td>{e.position ?? "—"}</td>
                <td>{seed ?? "—"}</td>
                <td className={diff === null ? "" : diff < 0 ? "diff-positive" : diff > 0 ? "diff-negative" : ""}>
                  {diff === null ? "—" : diff === 0 ? "=" : diff > 0 ? `+${diff}` : `${diff}`}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

interface Props {
  finals: Final[];
}

export function FinalsTable({ finals }: Props) {
  const [sorting, setSorting] = useState<SortingState>([{ id: "year", desc: true }]);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const rows = useMemo(() => buildRows(finals), [finals]);

  const columns = useMemo<ColumnDef<TableRow>[]>(
    () => [
      {
        id: "expand",
        header: "",
        cell: ({ row }) => (
          <button
            className="expand-btn"
            onClick={() => {
              const key = row.original.event_id;
              setExpanded((prev) => {
                const next = new Set(prev);
                if (next.has(key)) next.delete(key);
                else next.add(key);
                return next;
              });
            }}
            type="button"
          >
            {expanded.has(row.original.event_id) ? "▲" : "▼"}
          </button>
        ),
        enableSorting: false,
        size: 32,
      },
      { accessorKey: "competition", header: "Competition", size: 160 },
      { accessorKey: "year", header: "Year", size: 60 },
      { accessorKey: "location", header: "Location", size: 120 },
      {
        accessorKey: "pool",
        header: "Pool",
        size: 64,
        cell: ({ getValue }) => <span className="badge">{getValue() as string}</span>,
      },
      { accessorKey: "event", header: "Event", size: 180 },
      {
        accessorKey: "gender",
        header: "Gender",
        size: 72,
        cell: ({ getValue }) => (getValue() === "M" ? "Men" : getValue() === "F" ? "Women" : "Mixed"),
      },
      {
        id: "isRelay",
        accessorKey: "is_relay",
        header: "Relay",
        size: 60,
        cell: ({ getValue }) => (getValue() ? <span className="badge badge--relay">Relay</span> : null),
      },
      { accessorKey: "winner", header: "Winner", size: 160 },
      {
        accessorKey: "winnerNationality",
        header: "NAT",
        size: 52,
      },
      {
        accessorKey: "winnerLane",
        header: "Lane",
        size: 56,
        cell: ({ getValue }) => {
          const lane = getValue() as number;
          return lane > 0 ? <span className={`lane-badge lane-badge--${lane}`}>{lane}</span> : "—";
        },
      },
    ],
    [expanded]
  );

  const table = useReactTable({
    data: rows,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 25 } },
  });

  if (finals.length === 0) {
    return <p className="table-empty">No finals match the current filters.</p>;
  }

  return (
    <div className="table-container">
      <div className="table-scroll">
        <table className="finals-table">
          <thead>
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((header) => (
                  <th
                    key={header.id}
                    style={{ width: header.getSize() }}
                    onClick={header.column.getToggleSortingHandler()}
                    className={header.column.getCanSort() ? "sortable" : ""}
                  >
                    {flexRender(header.column.columnDef.header, header.getContext())}
                    {header.column.getIsSorted() === "asc" ? " ↑" : header.column.getIsSorted() === "desc" ? " ↓" : ""}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <>
                <tr key={row.id} className="data-row">
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
                {expanded.has(row.original.event_id) && (
                  <tr key={`${row.id}-sub`} className="sub-row">
                    <td colSpan={columns.length}>
                      <EntrySubRow final={row.original} />
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <button onClick={() => table.setPageIndex(0)} disabled={!table.getCanPreviousPage()} type="button">«</button>
        <button onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()} type="button">‹</button>
        <span>
          Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
        </span>
        <button onClick={() => table.nextPage()} disabled={!table.getCanNextPage()} type="button">›</button>
        <button onClick={() => table.setPageIndex(table.getPageCount() - 1)} disabled={!table.getCanNextPage()} type="button">»</button>
        <select
          value={table.getState().pagination.pageSize}
          onChange={(e) => table.setPageSize(Number(e.target.value))}
        >
          {[25, 50, 100].map((s) => (
            <option key={s} value={s}>Show {s}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
