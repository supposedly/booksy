import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { PermsComponent } from '../attrs/perms.component';
import { LocksComponent } from '../attrs/locks.component';
import { LimitsComponent } from '../attrs/limits.component';

import { MediaTypeService } from '../media-type.service';
import { LocationService } from '../location.service';

import { Globals } from '../globals';
  
  /* --------------------------------------- */
 // The media-type list component at /types //
/* --------------------------------------- */

@Component({
  selector: 'app-mgmt-media-types',
  template: `
    <button routerLink="./new">New type</button> <whatsthis [ident]="9"></whatsthis>
    <p *ngIf="msg">{{msg}}</p>
    <ul>
      <li *ngFor="let mtype of globals.locMediaTypes; let i = index" routerLink="./{{mtype.name}}">
        {{mtype.name}}
        <span (click)="deleteType(mtype.name, i)">Ⓧ</span>
      </li>
    </ul>
  `,
  styleUrls: ['./mgmt-media-types.component.css'],
})
export class MgmtMediaTypesComponent {
  mtypes: any = [];
  msg = '';
  
  constructor(
    public globals: Globals,
    private mTypeService: MediaTypeService
  ) {}
  
  deleteType(name, i) {
    this.mTypeService.delete(name)
      .subscribe();
    this.globals.locMediaTypes.splice(i, 1);
  }
}

@Component({
  selector: 'app-media-type-detail',
  template: `
  <p>{{msg}}</p>
  <button (click)="location.back()">Go back</button>
  <h2>{{name}}</h2>
  Name:
  <br/>
  <input type="text" [value]="name" [(ngModel)]="name"/>
  <br/>
  Unit of length (e.g. "pages" or "minutes"):
  <br/>
  <input type="text" [value]="unit" [(ngModel)]="unit"/>
  <form name="media-type-information" (ngSubmit)="submit()">
     <app-limits [arr]="maxArr" auxiliary></app-limits>
     <input type="submit" value="Submit"/>
  </form>
  `,
  styles: ['']
})
export class MediaTypeDetailComponent implements OnInit {
  maxArr: any = [];
  initialName: string;
  name: string;
  unit: string;
  msg = '';
  
  @ViewChild(LimitsComponent) private limits: LimitsComponent;
  
  constructor(
    public globals: Globals,
    public location: Location,
    private route: ActivatedRoute,
    private mTypeService: MediaTypeService
  ) {}
  
  ngOnInit() {
    this.initialName = this.name = this.route.snapshot.paramMap.get('name');
    if (this.initialName === 'new') {
      this.name = '';
      this.maxArr = null;
    } else {
      this.getInfo();
    }
  }
  
  getInfo() {
    this.mTypeService.info(this.name)
      .subscribe(
        resp => {
          this.maxArr = resp.type.limits;
          this.unit = resp.type.unit;
        }
      );
  }
  
  submit() {
    const maxArr = {}; // initialize to properly copy attrs to:
    for (const i of Object.keys(this.limits.arr.names)) {
      maxArr[i] = this.limits.overrideArr.names[i] ? this.limits.overrideArr.names[i] : this.limits.arr.names[i];
    }
    
    if (this.initialName === 'new') {
      this.mTypeService.add(maxArr, this.name, this.unit)
        .subscribe(
          _ => {
            this.initialName = this.name;
            this.globals.locMediaTypes.push({name: this.name, limits: maxArr});
            this.msg = 'Successfully created.';
          },
          err => this.msg = err.error ? err.error : 'Not allowed!'
        );
    } else {
      this.mTypeService.edit(this.initialName, maxArr, this.name, this.unit)
        .subscribe(
          _ => this.msg = 'Successfully edited.',
          err => this.msg = err.error ? err.error : 'Not allowed!',
          () => this.mTypeService.all() // refresh global list of media types
                  .subscribe(res => this.globals.locMediaTypes = res.types.map((dict, _) => dict))
        );
    }
  }
}
