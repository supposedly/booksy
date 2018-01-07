import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MgmtHeaderComponent } from './mgmt-header.component';

describe('MgmtHeaderComponent', () => {
  let component: MgmtHeaderComponent;
  let fixture: ComponentFixture<MgmtHeaderComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MgmtHeaderComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MgmtHeaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
